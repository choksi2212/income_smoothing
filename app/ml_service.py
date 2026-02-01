import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import (
    Transaction, AIFeature, CashflowPrediction, IncomeSource,
    SmoothingBuffer, WeeklyRelease, AIInsight, ModelVersion, ModelMetric,
    RiskLevel, InsightType, InsightSeverity, TransactionType
)
import pytz
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

IST = pytz.timezone('Asia/Kolkata')


class MLService:
    """Core ML service for income prediction and analysis"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def preprocess_transactions(self, user_id: str, months: int = 6) -> pd.DataFrame:
        """
        Preprocess transaction data for ML
        Returns clean DataFrame with IST timezone
        """
        cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
        
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.txn_timestamp >= cutoff_date
        ).order_by(Transaction.txn_timestamp).all()
        
        if not transactions:
            return pd.DataFrame()
        
        data = []
        for txn in transactions:
            data.append({
                'timestamp': txn.txn_timestamp,
                'amount': float(txn.amount_inr),
                'type': txn.txn_type.value,
                'is_income': txn.is_income,
                'category': txn.merchant_category.value,
                'balance': float(txn.balance_after_txn)
            })
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Remove extreme outliers using IQR
        Q1 = df['amount'].quantile(0.25)
        Q3 = df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        df = df[(df['amount'] >= lower_bound) & (df['amount'] <= upper_bound)]
        
        return df
    
    def extract_features(self, user_id: str) -> None:
        """
        Extract weekly features and store in ai_features table
        """
        df = self.preprocess_transactions(user_id, months=6)
        
        if df.empty:
            return
        
        df['week_start'] = df['timestamp'].dt.to_period('W').apply(lambda r: r.start_time)
        
        for week_start, week_data in df.groupby('week_start'):
            income_data = week_data[week_data['is_income'] == True]
            expense_data = week_data[week_data['is_income'] == False]
            
            total_income = income_data['amount'].sum()
            total_expense = expense_data['amount'].sum()
            net_cashflow = total_income - total_expense
            
            # Income metrics
            avg_daily_income = total_income / 7
            income_std = income_data['amount'].std() if len(income_data) > 1 else 0
            income_volatility = (income_std / avg_daily_income) if avg_daily_income > 0 else 0
            
            days_with_income = income_data['timestamp'].dt.date.nunique()
            days_without_income = 7 - days_with_income
            
            # Income source analysis
            income_sources = income_data['category'].value_counts()
            income_source_count = len(income_sources)
            top_source_pct = (income_sources.iloc[0] / total_income * 100) if len(income_sources) > 0 else 0
            
            # Expense metrics
            avg_daily_expense = total_expense / 7
            expense_std = expense_data['amount'].std() if len(expense_data) > 1 else 0
            
            # Check if feature already exists
            existing = self.db.query(AIFeature).filter(
                AIFeature.user_id == user_id,
                AIFeature.week_start_date == week_start
            ).first()
            
            if existing:
                existing.total_income_inr = Decimal(str(total_income))
                existing.total_expense_inr = Decimal(str(total_expense))
                existing.net_cashflow_inr = Decimal(str(net_cashflow))
                existing.avg_daily_income = Decimal(str(avg_daily_income))
                existing.income_std_dev = Decimal(str(income_std))
                existing.income_volatility_ratio = Decimal(str(income_volatility))
                existing.days_with_income = days_with_income
                existing.days_without_income = days_without_income
                existing.income_source_count = income_source_count
                existing.top_income_source_pct = Decimal(str(top_source_pct))
                existing.avg_daily_expense = Decimal(str(avg_daily_expense))
                existing.expense_std_dev = Decimal(str(expense_std))
            else:
                feature = AIFeature(
                    user_id=user_id,
                    week_start_date=week_start,
                    total_income_inr=Decimal(str(total_income)),
                    total_expense_inr=Decimal(str(total_expense)),
                    net_cashflow_inr=Decimal(str(net_cashflow)),
                    avg_daily_income=Decimal(str(avg_daily_income)),
                    income_std_dev=Decimal(str(income_std)),
                    income_volatility_ratio=Decimal(str(income_volatility)),
                    days_with_income=days_with_income,
                    days_without_income=days_without_income,
                    income_source_count=income_source_count,
                    top_income_source_pct=Decimal(str(top_source_pct)),
                    avg_daily_expense=Decimal(str(avg_daily_expense)),
                    expense_std_dev=Decimal(str(expense_std))
                )
                self.db.add(feature)
        
        self.db.commit()
    
    def calculate_income_stability_score(self, user_id: str) -> Decimal:
        """
        Calculate income stability score (0-1)
        Higher = more stable
        """
        features = self.db.query(AIFeature).filter(
            AIFeature.user_id == user_id
        ).order_by(AIFeature.week_start_date.desc()).limit(12).all()
        
        if not features:
            return Decimal('0.5')
        
        # Coefficient of variation (lower is better)
        incomes = [float(f.total_income_inr) for f in features]
        if len(incomes) < 2:
            return Decimal('0.5')
        
        mean_income = np.mean(incomes)
        std_income = np.std(incomes)
        cv = std_income / mean_income if mean_income > 0 else 1.0
        
        # Source concentration (lower is better)
        avg_top_source_pct = np.mean([float(f.top_income_source_pct) for f in features])
        concentration_penalty = avg_top_source_pct / 100.0
        
        # Rolling variance penalty
        rolling_var = np.var(incomes)
        var_penalty = min(rolling_var / (mean_income ** 2), 1.0) if mean_income > 0 else 1.0
        
        # Combine scores (inverse relationship)
        stability = 1.0 - (0.4 * cv + 0.3 * concentration_penalty + 0.3 * var_penalty)
        stability = max(0.0, min(1.0, stability))
        
        return Decimal(str(round(stability, 2)))
    
    def predict_cashflow_rolling_mean(self, user_id: str, days: int) -> Dict:
        """
        Primary prediction method: Rolling mean + std
        Conservative and explainable
        """
        df = self.preprocess_transactions(user_id, months=6)
        
        if df.empty or len(df) < 14:
            return {
                'expected_inflow': 0,
                'expected_outflow': 0,
                'net_cashflow': 0,
                'lower_bound': 0,
                'upper_bound': 0,
                'risk_level': RiskLevel.HIGH,
                'confidence': 0.3
            }
        
        # Separate income and expenses
        income_df = df[df['is_income'] == True].copy()
        expense_df = df[df['is_income'] == False].copy()
        
        # Daily aggregation
        income_df['date'] = income_df['timestamp'].dt.date
        expense_df['date'] = expense_df['timestamp'].dt.date
        
        daily_income = income_df.groupby('date')['amount'].sum()
        daily_expense = expense_df.groupby('date')['amount'].sum()
        
        # Rolling statistics (30-day window)
        window = min(30, len(daily_income))
        
        mean_daily_income = daily_income.rolling(window=window, min_periods=7).mean().iloc[-1]
        std_daily_income = daily_income.rolling(window=window, min_periods=7).std().iloc[-1]
        
        mean_daily_expense = daily_expense.rolling(window=window, min_periods=7).mean().iloc[-1]
        std_daily_expense = daily_expense.rolling(window=window, min_periods=7).std().iloc[-1]
        
        # Project forward
        expected_inflow = mean_daily_income * days
        expected_outflow = mean_daily_expense * days
        net_cashflow = expected_inflow - expected_outflow
        
        # Conservative bounds (2 std devs)
        lower_bound_income = max(0, mean_daily_income - 2 * std_daily_income) * days
        upper_bound_income = (mean_daily_income + 2 * std_daily_income) * days
        
        lower_bound = lower_bound_income - expected_outflow
        upper_bound = upper_bound_income - expected_outflow
        
        # Risk assessment
        volatility = std_daily_income / mean_daily_income if mean_daily_income > 0 else 1.0
        if volatility < 0.3:
            risk_level = RiskLevel.LOW
            confidence = 0.85
        elif volatility < 0.6:
            risk_level = RiskLevel.MEDIUM
            confidence = 0.70
        else:
            risk_level = RiskLevel.HIGH
            confidence = 0.50
        
        return {
            'expected_inflow': float(expected_inflow),
            'expected_outflow': float(expected_outflow),
            'net_cashflow': float(net_cashflow),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'risk_level': risk_level,
            'confidence': confidence
        }
    
    def predict_cashflow_arima(self, user_id: str, days: int) -> Optional[Dict]:
        """
        Secondary prediction: ARIMA (only if >= 180 days data)
        """
        df = self.preprocess_transactions(user_id, months=6)
        
        if df.empty or len(df) < 180:
            return None
        
        try:
            income_df = df[df['is_income'] == True].copy()
            income_df['date'] = income_df['timestamp'].dt.date
            daily_income = income_df.groupby('date')['amount'].sum()
            
            # Fit ARIMA
            model = ARIMA(daily_income, order=(1, 1, 1))
            fitted = model.fit()
            
            # Forecast
            forecast = fitted.forecast(steps=days)
            forecast_mean = forecast.mean()
            forecast_std = forecast.std()
            
            expected_inflow = forecast.sum()
            lower_bound = max(0, forecast_mean - 2 * forecast_std) * days
            upper_bound = (forecast_mean + 2 * forecast_std) * days
            
            # Expenses (use rolling mean)
            expense_df = df[df['is_income'] == False].copy()
            expense_df['date'] = expense_df['timestamp'].dt.date
            daily_expense = expense_df.groupby('date')['amount'].sum()
            mean_expense = daily_expense.mean()
            expected_outflow = mean_expense * days
            
            return {
                'expected_inflow': float(expected_inflow),
                'expected_outflow': float(expected_outflow),
                'net_cashflow': float(expected_inflow - expected_outflow),
                'lower_bound': float(lower_bound - expected_outflow),
                'upper_bound': float(upper_bound - expected_outflow),
                'risk_level': RiskLevel.MEDIUM,
                'confidence': 0.75
            }
        except Exception as e:
            print(f"ARIMA failed: {e}")
            return None
    
    def predict_cashflow(self, user_id: str, days: int) -> Dict:
        """
        Main prediction method - tries ARIMA, falls back to rolling mean
        """
        # Try ARIMA first if enough data
        arima_result = self.predict_cashflow_arima(user_id, days)
        if arima_result:
            return {**arima_result, 'model_used': 'ARIMA'}
        
        # Fall back to rolling mean
        rolling_result = self.predict_cashflow_rolling_mean(user_id, days)
        return {**rolling_result, 'model_used': 'RollingMean'}
    
    def save_prediction(self, user_id: str, days: int) -> CashflowPrediction:
        """
        Generate and save cashflow prediction
        """
        prediction_data = self.predict_cashflow(user_id, days)
        
        prediction = CashflowPrediction(
            user_id=user_id,
            prediction_date=datetime.utcnow(),
            prediction_window_days=days,
            expected_inflow_inr=Decimal(str(prediction_data['expected_inflow'])),
            expected_outflow_inr=Decimal(str(prediction_data['expected_outflow'])),
            net_cashflow_inr=Decimal(str(prediction_data['net_cashflow'])),
            lower_bound_inr=Decimal(str(prediction_data['lower_bound'])),
            upper_bound_inr=Decimal(str(prediction_data['upper_bound'])),
            risk_level=prediction_data['risk_level'],
            model_used=prediction_data['model_used'],
            confidence_score=Decimal(str(prediction_data['confidence']))
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        return prediction
    
    def calculate_safe_to_spend(self, user_id: str) -> Dict:
        """
        Calculate conservative safe-to-spend limits
        NOT ML - pure rule-based calculation
        """
        # Get 7-day prediction
        prediction_7d = self.predict_cashflow(user_id, 7)
        
        # Get buffer balance
        buffer = self.db.query(SmoothingBuffer).filter(
            SmoothingBuffer.user_id == user_id
        ).first()
        
        buffer_balance = float(buffer.buffer_balance_inr) if buffer else 0
        
        # Get fixed expenses from profile
        from app.models import UserProfile
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        monthly_fixed = float(profile.monthly_fixed_expenses_inr) if profile else 0
        weekly_fixed = monthly_fixed / 4.33
        
        # Worst-case income (lower bound)
        worst_case_income_7d = max(0, prediction_7d['lower_bound'])
        
        # Volatility multiplier (more volatile = more conservative)
        features = self.db.query(AIFeature).filter(
            AIFeature.user_id == user_id
        ).order_by(AIFeature.week_start_date.desc()).limit(4).all()
        
        if features:
            avg_volatility = np.mean([float(f.income_volatility_ratio) for f in features])
            volatility_multiplier = 1.0 + min(avg_volatility, 1.0)
        else:
            volatility_multiplier = 1.5
        
        # Safe weekly spend = (worst case income + buffer) / volatility - fixed expenses
        available = worst_case_income_7d + buffer_balance
        safe_weekly = max(0, (available / volatility_multiplier) - weekly_fixed)
        safe_daily = safe_weekly / 7
        
        # Predict cash exhaustion
        if safe_daily > 0:
            days_until_exhaustion = buffer_balance / safe_daily
            exhaustion_date = datetime.utcnow() + timedelta(days=int(days_until_exhaustion))
        else:
            exhaustion_date = datetime.utcnow()
        
        return {
            'daily_safe_spend_inr': round(safe_daily, 2),
            'weekly_safe_spend_inr': round(safe_weekly, 2),
            'predicted_cash_exhaustion_date': exhaustion_date,
            'buffer_balance_inr': buffer_balance,
            'worst_case_income_7d': worst_case_income_7d,
            'fixed_expenses_weekly': weekly_fixed,
            'volatility_multiplier': volatility_multiplier,
            'explanation': f"Based on worst-case income of ₹{worst_case_income_7d:.0f}, buffer of ₹{buffer_balance:.0f}, and volatility factor of {volatility_multiplier:.2f}x"
        }
    
    def update_income_sources(self, user_id: str) -> None:
        """
        Analyze and update income sources
        """
        df = self.preprocess_transactions(user_id, months=3)
        
        if df.empty:
            return
        
        income_df = df[df['is_income'] == True]
        
        # Group by category
        source_stats = income_df.groupby('category').agg({
            'amount': ['sum', 'mean', 'std', 'count']
        }).reset_index()
        
        source_stats.columns = ['category', 'total', 'mean', 'std', 'count']
        
        total_income = source_stats['total'].sum()
        
        # Delete old sources
        self.db.query(IncomeSource).filter(IncomeSource.user_id == user_id).delete()
        
        for _, row in source_stats.iterrows():
            contribution_pct = (row['total'] / total_income * 100) if total_income > 0 else 0
            
            # Stability score (inverse of coefficient of variation)
            cv = row['std'] / row['mean'] if row['mean'] > 0 else 1.0
            stability = max(0, 1.0 - cv)
            
            # Last payment
            last_payment = income_df[income_df['category'] == row['category']]['timestamp'].max()
            
            source = IncomeSource(
                user_id=user_id,
                source_name=row['category'],
                source_category=row['category'],
                avg_monthly_inr=Decimal(str(row['mean'] * 30)),
                contribution_pct=Decimal(str(contribution_pct)),
                stability_score=Decimal(str(stability)),
                last_payment_date=last_payment
            )
            self.db.add(source)
        
        self.db.commit()
    
    def generate_insights(self, user_id: str) -> List[AIInsight]:
        """
        Generate rule-based AI insights
        """
        insights = []
        
        # Get recent features
        features = self.db.query(AIFeature).filter(
            AIFeature.user_id == user_id
        ).order_by(AIFeature.week_start_date.desc()).limit(8).all()
        
        if not features:
            return insights
        
        latest = features[0]
        
        # 1. Volatility spike
        if float(latest.income_volatility_ratio) > 0.7:
            insights.append(AIInsight(
                user_id=user_id,
                insight_type=InsightType.VOLATILITY_SPIKE,
                severity=InsightSeverity.WARNING,
                explanation_text=f"Your income volatility is high at {float(latest.income_volatility_ratio):.1%}. Consider diversifying income sources.",
                supporting_metrics={
                    'volatility_ratio': float(latest.income_volatility_ratio),
                    'income_std_dev': float(latest.income_std_dev),
                    'avg_income': float(latest.avg_daily_income)
                }
            ))
        
        # 2. Source concentration
        if float(latest.top_income_source_pct) > 60:
            insights.append(AIInsight(
                user_id=user_id,
                insight_type=InsightType.SOURCE_CONCENTRATION,
                severity=InsightSeverity.WARNING,
                explanation_text=f"Your top income source accounts for {float(latest.top_income_source_pct):.0f}% of income. Reduce client concentration.",
                supporting_metrics={
                    'top_source_pct': float(latest.top_income_source_pct),
                    'source_count': latest.income_source_count
                }
            ))
        
        # 3. Expense creep
        if len(features) >= 4:
            recent_expense = np.mean([float(f.avg_daily_expense) for f in features[:4]])
            older_expense = np.mean([float(f.avg_daily_expense) for f in features[4:]])
            
            if recent_expense > older_expense * 1.2:
                insights.append(AIInsight(
                    user_id=user_id,
                    insight_type=InsightType.EXPENSE_CREEP,
                    severity=InsightSeverity.WARNING,
                    explanation_text=f"Your expenses increased by {((recent_expense/older_expense - 1) * 100):.0f}% recently.",
                    supporting_metrics={
                        'recent_avg': recent_expense,
                        'older_avg': older_expense,
                        'increase_pct': (recent_expense/older_expense - 1) * 100
                    }
                ))
        
        # 4. Low income warning
        if float(latest.total_income_inr) < 5000:
            insights.append(AIInsight(
                user_id=user_id,
                insight_type=InsightType.LOW_INCOME_WARNING,
                severity=InsightSeverity.CRITICAL,
                explanation_text=f"Low income week detected: ₹{float(latest.total_income_inr):.0f}. Buffer may be needed.",
                supporting_metrics={
                    'weekly_income': float(latest.total_income_inr),
                    'days_with_income': latest.days_with_income
                }
            ))
        
        # 5. Positive trend
        if len(features) >= 4:
            recent_income = np.mean([float(f.total_income_inr) for f in features[:4]])
            older_income = np.mean([float(f.total_income_inr) for f in features[4:]])
            
            if older_income > 0 and recent_income > older_income * 1.15:
                increase_pct = (recent_income/older_income - 1) * 100
                insights.append(AIInsight(
                    user_id=user_id,
                    insight_type=InsightType.POSITIVE_TREND,
                    severity=InsightSeverity.INFO,
                    explanation_text=f"Income trending up by {increase_pct:.0f}%. Great work!",
                    supporting_metrics={
                        'recent_avg': recent_income,
                        'older_avg': older_income,
                        'increase_pct': increase_pct
                    }
                ))
        
        # Save insights
        for insight in insights:
            self.db.add(insight)
        
        self.db.commit()
        
        return insights
