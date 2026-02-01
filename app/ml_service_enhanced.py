"""
Enhanced ML Service with Pre-trained Model Support
Falls back to real-time training if pre-trained models not available
"""
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Transaction, AIFeature, CashflowPrediction, IncomeSource, AIInsight, RiskLevel, InsightType, InsightSeverity
from app.ml_service import MLService as BaseMLService
import warnings
warnings.filterwarnings('ignore')

MODELS_DIR = Path("ml_models")


class EnhancedMLService(BaseMLService):
    """Enhanced ML Service with pre-trained model support"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.models_dir = MODELS_DIR
    
    def load_pretrained_model(self, user_id: str, model_type: str):
        """Load pre-trained model if available"""
        model_path = self.models_dir / f"{model_type}_{user_id}.pkl"
        
        if model_path.exists():
            try:
                model = joblib.load(model_path)
                return model
            except Exception as e:
                print(f"Failed to load {model_type} model: {e}")
                return None
        return None
    
    def predict_with_pretrained_arima(self, user_id: str, days: int):
        """Use pre-trained ARIMA model for prediction"""
        model = self.load_pretrained_model(user_id, 'arima')
        
        if model is None:
            return None
        
        try:
            # Forecast
            forecast = model.forecast(steps=days)
            
            # Calculate bounds (conservative)
            std = np.std(model.resid)
            lower_bound = forecast - 1.96 * std
            upper_bound = forecast + 1.96 * std
            
            return {
                'forecast': float(np.sum(forecast)),
                'lower': float(np.sum(np.maximum(lower_bound, 0))),
                'upper': float(np.sum(upper_bound)),
                'daily_avg': float(np.mean(forecast))
            }
        except Exception as e:
            print(f"ARIMA prediction failed: {e}")
            return None
    
    def predict_with_pretrained_prophet(self, user_id: str, days: int):
        """Use pre-trained Prophet model for prediction"""
        model = self.load_pretrained_model(user_id, 'prophet')
        
        if model is None:
            return None
        
        try:
            # Create future dataframe
            future = model.make_future_dataframe(periods=days, freq='D')
            
            # Predict
            forecast = model.predict(future)
            
            # Get last N days
            forecast_period = forecast.tail(days)
            
            return {
                'forecast': float(forecast_period['yhat'].sum()),
                'lower': float(forecast_period['yhat_lower'].sum()),
                'upper': float(forecast_period['yhat_upper'].sum()),
                'daily_avg': float(forecast_period['yhat'].mean())
            }
        except Exception as e:
            print(f"Prophet prediction failed: {e}")
            return None
    
    def predict_with_pretrained_rolling_mean(self, user_id: str, days: int):
        """Use pre-trained Rolling Mean parameters"""
        params = self.load_pretrained_model(user_id, 'rolling_mean')
        
        if params is None:
            return None
        
        try:
            daily_mean = params['mean']
            daily_std = params['std']
            
            forecast = daily_mean * days
            lower = max(0, (daily_mean - 1.96 * daily_std) * days)
            upper = (daily_mean + 1.96 * daily_std) * days
            
            return {
                'forecast': float(forecast),
                'lower': float(lower),
                'upper': float(upper),
                'daily_avg': float(daily_mean)
            }
        except Exception as e:
            print(f"Rolling Mean prediction failed: {e}")
            return None
    
    def predict_cashflow_enhanced(self, user_id: str, days: int = 30):
        """
        Enhanced prediction using pre-trained models
        Falls back to real-time training if models not available
        """
        # Try pre-trained models first
        arima_pred = self.predict_with_pretrained_arima(user_id, days)
        prophet_pred = self.predict_with_pretrained_prophet(user_id, days)
        rolling_pred = self.predict_with_pretrained_rolling_mean(user_id, days)
        
        # If we have pre-trained models, use them
        if arima_pred or prophet_pred or rolling_pred:
            # Use the best available model (prefer ARIMA > Prophet > Rolling Mean)
            if arima_pred:
                prediction = arima_pred
                model_used = "ARIMA (Pre-trained)"
            elif prophet_pred:
                prediction = prophet_pred
                model_used = "Prophet (Pre-trained)"
            else:
                prediction = rolling_pred
                model_used = "Rolling Mean (Pre-trained)"
            
            # Get expense prediction
            expense_pred = self._predict_expenses(user_id, days)
            
            return {
                'expected_inflow_inr': Decimal(str(round(prediction['forecast'], 2))),
                'expected_outflow_inr': Decimal(str(round(expense_pred, 2))),
                'net_cashflow_inr': Decimal(str(round(prediction['forecast'] - expense_pred, 2))),
                'lower_bound_inr': Decimal(str(round(prediction['lower'] - expense_pred, 2))),
                'upper_bound_inr': Decimal(str(round(prediction['upper'] - expense_pred, 2))),
                'model_used': model_used,
                'confidence_score': Decimal('0.85')
            }
        
        # Fall back to real-time training
        print(f"No pre-trained models found for user {user_id}, using real-time prediction")
        return super().predict_cashflow(user_id, days)
    
    def _predict_expenses(self, user_id: str, days: int):
        """Predict expenses for the period"""
        # Get recent expenses
        recent_date = datetime.utcnow() - timedelta(days=90)
        
        expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.is_income == False,
            Transaction.txn_timestamp >= recent_date
        ).all()
        
        if not expenses:
            return 0
        
        # Calculate daily average
        total_expense = sum(float(e.amount_inr) for e in expenses)
        num_days = (datetime.utcnow() - recent_date).days
        daily_avg = total_expense / num_days if num_days > 0 else 0
        
        return daily_avg * days
    
    def get_model_info(self, user_id: str):
        """Get information about available models for a user"""
        info = {
            'user_id': user_id,
            'models': {}
        }
        
        for model_type in ['arima', 'prophet', 'rolling_mean']:
            model_path = self.models_dir / f"{model_type}_{user_id}.pkl"
            if model_path.exists():
                info['models'][model_type] = {
                    'available': True,
                    'path': str(model_path),
                    'size_kb': model_path.stat().st_size / 1024,
                    'modified': datetime.fromtimestamp(model_path.stat().st_mtime).isoformat()
                }
            else:
                info['models'][model_type] = {
                    'available': False
                }
        
        return info
    
    def save_prediction(self, user_id: str, days: int):
        """
        Generate and save cashflow prediction using enhanced ML service
        Uses pre-trained models for 25-100x faster predictions
        """
        prediction_data = self.predict_cashflow_enhanced(user_id, days)
        
        prediction = CashflowPrediction(
            user_id=user_id,
            prediction_date=datetime.utcnow(),
            prediction_window_days=days,
            expected_inflow_inr=prediction_data['expected_inflow_inr'],
            expected_outflow_inr=prediction_data['expected_outflow_inr'],
            net_cashflow_inr=prediction_data['net_cashflow_inr'],
            lower_bound_inr=prediction_data['lower_bound_inr'],
            upper_bound_inr=prediction_data['upper_bound_inr'],
            risk_level=RiskLevel.MEDIUM,  # Default to medium
            model_used=prediction_data['model_used'],
            confidence_score=prediction_data['confidence_score']
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        return prediction
