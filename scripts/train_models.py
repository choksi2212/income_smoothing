"""
ML Model Training Pipeline
Trains ARIMA and Prophet models for all users with sufficient data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, Transaction, CashflowPrediction
from app.ml_service import MLService
from sqlalchemy import func
from datetime import datetime, timedelta
import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

# Create models directory
MODELS_DIR = Path("ml_models")
MODELS_DIR.mkdir(exist_ok=True)

def get_users_with_sufficient_data(db, min_transactions=180):
    """Get users with enough data for training"""
    users = db.query(
        User.user_id,
        User.email,
        func.count(Transaction.transaction_id).label('txn_count')
    ).join(
        Transaction, User.user_id == Transaction.user_id
    ).group_by(
        User.user_id, User.email
    ).having(
        func.count(Transaction.transaction_id) >= min_transactions
    ).all()
    
    return users


def prepare_time_series_data(db, user_id):
    """Prepare time series data for training"""
    # Get all transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.is_income == True
    ).order_by(Transaction.txn_timestamp).all()
    
    if len(transactions) < 30:
        return None
    
    # Create daily income series
    df = pd.DataFrame([{
        'date': txn.txn_timestamp.date(),
        'amount': float(txn.amount_inr)
    } for txn in transactions])
    
    # Group by date and sum
    daily_income = df.groupby('date')['amount'].sum().reset_index()
    daily_income.columns = ['ds', 'y']
    daily_income['ds'] = pd.to_datetime(daily_income['ds'])
    
    # Fill missing dates with 0
    date_range = pd.date_range(
        start=daily_income['ds'].min(),
        end=daily_income['ds'].max(),
        freq='D'
    )
    
    full_df = pd.DataFrame({'ds': date_range})
    full_df = full_df.merge(daily_income, on='ds', how='left')
    full_df['y'] = full_df['y'].fillna(0)
    
    return full_df


def train_arima_model(data, user_id):
    """Train ARIMA model for a user"""
    try:
        print(f"  Training ARIMA model...")
        
        # Use only the income values
        y = data['y'].values
        
        if len(y) < 60:
            print(f"    WARNING Insufficient data for ARIMA (need 60+ days)")
            return None
        
        # Fit ARIMA model with simpler order to avoid issues
        # Using (3,1,2) which is more stable than (5,1,0)
        model = ARIMA(y, order=(3, 1, 2))
        fitted_model = model.fit()
        
        # Save model
        model_path = MODELS_DIR / f"arima_{user_id}.pkl"
        joblib.dump(fitted_model, model_path)
        
        # Calculate metrics using in-sample predictions
        # Get predictions for the entire series
        predictions = fitted_model.predict(start=1, end=len(y)-1)
        actual = y[1:]  # Skip first value due to differencing
        
        # Ensure same length
        min_len = min(len(predictions), len(actual))
        predictions = predictions[:min_len]
        actual = actual[:min_len]
        
        mae = np.mean(np.abs(predictions - actual))
        
        print(f"    SUCCESS ARIMA trained - MAE: Rs.{mae:.2f}")
        return {
            'model_type': 'ARIMA',
            'mae': mae,
            'model_path': str(model_path),
            'params': '(3,1,2)'
        }
    except Exception as e:
        print(f"    WARNING ARIMA training skipped: {str(e)[:80]}")
        return None


def train_prophet_model(data, user_id):
    """Train Prophet model for a user"""
    try:
        print(f"  Training Prophet model...")
        
        if len(data) < 60:
            print(f"    WARNING Insufficient data for Prophet (need 60+ days)")
            return None
        
        # Prophet requires specific column names
        prophet_data = data.copy()
        
        # Suppress all Prophet logging
        import logging
        logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
        logging.getLogger('prophet').setLevel(logging.ERROR)
        
        # Try to use Prophet without cmdstan (fallback to pystan)
        try:
            # First try with default backend
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=0.1,
                interval_width=0.95
            )
            
            # Fit model - suppress all output
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()
            
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model.fit(prophet_data)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            # Save model
            model_path = MODELS_DIR / f"prophet_{user_id}.pkl"
            joblib.dump(model, model_path)
            
            # Calculate metrics
            forecast = model.predict(prophet_data)
            mae = np.mean(np.abs(forecast['yhat'].values - prophet_data['y'].values))
            
            print(f"    SUCCESS Prophet trained - MAE: Rs.{mae:.2f}")
            return {
                'model_type': 'Prophet',
                'mae': mae,
                'model_path': str(model_path),
                'params': 'weekly_seasonality'
            }
            
        except Exception as inner_e:
            error_msg = str(inner_e).lower()
            # Check if it's a backend issue
            if any(x in error_msg for x in ['stan_backend', 'cmdstan', 'pystan', 'backend']):
                print(f"    WARNING Prophet backend not available, skipping")
                return None
            # For other errors, re-raise
            raise inner_e
            
    except Exception as e:
        print(f"    WARNING Prophet training skipped: {str(e)[:80]}")
        return None


def train_rolling_mean_model(data, user_id):
    """Train Rolling Mean model (simple baseline)"""
    try:
        print(f"  Training Rolling Mean model...")
        
        y = data['y'].values
        window = min(30, len(y) // 3)  # 30-day window or 1/3 of data
        
        # Calculate rolling mean
        rolling_mean = pd.Series(y).rolling(window=window, min_periods=1).mean()
        
        # Calculate MAE
        mae = np.mean(np.abs(rolling_mean.values - y))
        
        # Save parameters
        params = {
            'window': window,
            'mean': float(np.mean(y)),
            'std': float(np.std(y))
        }
        
        model_path = MODELS_DIR / f"rolling_mean_{user_id}.pkl"
        joblib.dump(params, model_path)
        
        print(f"    SUCCESS Rolling Mean trained - MAE: Rs.{mae:.2f}")
        return {
            'model_type': 'Rolling Mean',
            'mae': mae,
            'model_path': str(model_path),
            'params': f'window={window}'
        }
    except Exception as e:
        print(f"    WARNING Rolling Mean training failed: {str(e)[:80]}")
        return None


def save_model_metadata(db, user_id, model_info):
    """Save model metadata to database"""
    # You could create a ModelMetadata table to store this
    # For now, we'll just print it
    pass


def main():
    print("=" * 80)
    print("ML MODEL TRAINING PIPELINE")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    
    try:
        # Get users with sufficient data
        print("Finding users with sufficient data...")
        users = get_users_with_sufficient_data(db, min_transactions=180)
        print(f"   Found {len(users)} users with 180+ transactions")
        print()
        
        if len(users) == 0:
            print("WARNING: No users with sufficient data for training")
            return
        
        # Training statistics
        stats = {
            'total_users': len(users),
            'arima_success': 0,
            'prophet_success': 0,
            'rolling_mean_success': 0,
            'failed': 0
        }
        
        # Train models for each user
        for idx, user in enumerate(users, 1):
            user_id = str(user.user_id)
            email = user.email
            txn_count = user.txn_count
            
            print(f"[{idx}/{len(users)}] Training models for: {email}")
            print(f"   Transactions: {txn_count}")
            
            # Prepare data
            data = prepare_time_series_data(db, user.user_id)
            
            if data is None or len(data) < 30:
                print(f"   WARNING: Insufficient income data, skipping...")
                stats['failed'] += 1
                print()
                continue
            
            print(f"   Data points: {len(data)} days")
            
            # Train all three models
            arima_result = train_arima_model(data, user_id)
            if arima_result:
                stats['arima_success'] += 1
            
            prophet_result = train_prophet_model(data, user_id)
            if prophet_result:
                stats['prophet_success'] += 1
            
            rolling_result = train_rolling_mean_model(data, user_id)
            if rolling_result:
                stats['rolling_mean_success'] += 1
            
            if not (arima_result or prophet_result or rolling_result):
                stats['failed'] += 1
            
            print()
        
        # Print summary
        print("=" * 80)
        print("TRAINING COMPLETE!")
        print("=" * 80)
        print()
        print(f"Training Statistics:")
        print(f"   Total Users: {stats['total_users']}")
        print(f"   ARIMA Models: {stats['arima_success']} SUCCESS")
        print(f"   Prophet Models: {stats['prophet_success']} SUCCESS")
        print(f"   Rolling Mean Models: {stats['rolling_mean_success']} SUCCESS")
        print(f"   Failed: {stats['failed']} FAILED")
        print()
        print(f"Models saved in: {MODELS_DIR.absolute()}")
        print()
        
        # List saved models
        model_files = list(MODELS_DIR.glob("*.pkl"))
        print(f"Total model files: {len(model_files)}")
        print()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
