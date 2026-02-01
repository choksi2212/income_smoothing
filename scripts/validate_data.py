import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, Transaction, AIFeature, CashflowPrediction, IncomeSource, SmoothingBuffer
from sqlalchemy import func
from datetime import datetime, timedelta


def validate_and_report():
    """Validate generated data and create comprehensive report"""
    db = SessionLocal()
    
    print("=" * 80)
    print("DATA VALIDATION & STATISTICS REPORT")
    print("=" * 80)
    print(f"\nGenerated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80)
    
    # User Statistics
    print("\n📊 USER STATISTICS")
    print("-" * 80)
    
    total_users = db.query(func.count(User.user_id)).scalar()
    active_users = db.query(func.count(User.user_id)).filter(User.is_active == True).scalar()
    
    print(f"Total Users: {total_users}")
    print(f"Active Users: {active_users}")
    print(f"Inactive Users: {total_users - active_users}")
    
    # Transaction Statistics
    print("\n💰 TRANSACTION STATISTICS")
    print("-" * 80)
    
    total_transactions = db.query(func.count(Transaction.transaction_id)).scalar()
    total_income_txns = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.is_income == True
    ).scalar()
    total_expense_txns = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.is_income == False
    ).scalar()
    
    print(f"Total Transactions: {total_transactions:,}")
    print(f"Income Transactions: {total_income_txns:,} ({total_income_txns/total_transactions*100:.1f}%)")
    print(f"Expense Transactions: {total_expense_txns:,} ({total_expense_txns/total_transactions*100:.1f}%)")
    print(f"Avg Transactions per User: {total_transactions/total_users:.0f}")
    
    # Date range
    oldest_txn = db.query(func.min(Transaction.txn_timestamp)).scalar()
    newest_txn = db.query(func.max(Transaction.txn_timestamp)).scalar()
    
    if oldest_txn and newest_txn:
        date_range = (newest_txn - oldest_txn).days
        print(f"\nDate Range: {oldest_txn.strftime('%Y-%m-%d')} to {newest_txn.strftime('%Y-%m-%d')}")
        print(f"Total Days: {date_range}")
        print(f"Avg Transactions per Day: {total_transactions/date_range:.1f}")
    
    # Amount statistics
    total_income = db.query(func.sum(Transaction.amount_inr)).filter(
        Transaction.is_income == True
    ).scalar() or 0
    total_expenses = db.query(func.sum(Transaction.amount_inr)).filter(
        Transaction.is_income == False
    ).scalar() or 0
    
    print(f"\nTotal Income: ₹{total_income:,.2f}")
    print(f"Total Expenses: ₹{total_expenses:,.2f}")
    print(f"Net Cash Flow: ₹{total_income - total_expenses:,.2f}")
    print(f"Avg Income per Transaction: ₹{total_income/total_income_txns:,.2f}")
    print(f"Avg Expense per Transaction: ₹{total_expenses/total_expense_txns:,.2f}")
    
    # ML Features
    print("\n🧠 ML FEATURES")
    print("-" * 80)
    
    total_features = db.query(func.count(AIFeature.feature_id)).scalar()
    users_with_features = db.query(func.count(func.distinct(AIFeature.user_id))).scalar()
    
    print(f"Total Feature Records: {total_features:,}")
    print(f"Users with Features: {users_with_features}")
    print(f"Avg Features per User: {total_features/users_with_features:.1f}")
    
    # Predictions
    print("\n🔮 PREDICTIONS")
    print("-" * 80)
    
    total_predictions = db.query(func.count(CashflowPrediction.prediction_id)).scalar()
    users_with_predictions = db.query(func.count(func.distinct(CashflowPrediction.user_id))).scalar()
    
    predictions_7d = db.query(func.count(CashflowPrediction.prediction_id)).filter(
        CashflowPrediction.prediction_window_days == 7
    ).scalar()
    predictions_30d = db.query(func.count(CashflowPrediction.prediction_id)).filter(
        CashflowPrediction.prediction_window_days == 30
    ).scalar()
    predictions_60d = db.query(func.count(CashflowPrediction.prediction_id)).filter(
        CashflowPrediction.prediction_window_days == 60
    ).scalar()
    
    print(f"Total Predictions: {total_predictions}")
    print(f"Users with Predictions: {users_with_predictions}")
    print(f"  7-day predictions: {predictions_7d}")
    print(f"  30-day predictions: {predictions_30d}")
    print(f"  60-day predictions: {predictions_60d}")
    
    # Risk distribution
    risk_low = db.query(func.count(CashflowPrediction.prediction_id)).filter(
        CashflowPrediction.risk_level == 'low'
    ).scalar()
    risk_medium = db.query(func.count(CashflowPrediction.prediction_id)).filter(
        CashflowPrediction.risk_level == 'medium'
    ).scalar()
    risk_high = db.query(func.count(CashflowPrediction.prediction_id)).filter(
        CashflowPrediction.risk_level == 'high'
    ).scalar()
    
    print(f"\nRisk Distribution:")
    print(f"  Low Risk: {risk_low} ({risk_low/total_predictions*100:.1f}%)")
    print(f"  Medium Risk: {risk_medium} ({risk_medium/total_predictions*100:.1f}%)")
    print(f"  High Risk: {risk_high} ({risk_high/total_predictions*100:.1f}%)")
    
    # Income Sources
    print("\n💼 INCOME SOURCES")
    print("-" * 80)
    
    total_sources = db.query(func.count(IncomeSource.source_id)).scalar()
    users_with_sources = db.query(func.count(func.distinct(IncomeSource.user_id))).scalar()
    
    print(f"Total Income Sources: {total_sources}")
    print(f"Users with Sources: {users_with_sources}")
    print(f"Avg Sources per User: {total_sources/users_with_sources:.1f}")
    
    # Smoothing Buffers
    print("\n🔄 INCOME SMOOTHING")
    print("-" * 80)
    
    total_buffers = db.query(func.count(SmoothingBuffer.buffer_id)).scalar()
    total_buffer_balance = db.query(func.sum(SmoothingBuffer.buffer_balance_inr)).scalar() or 0
    total_deposited = db.query(func.sum(SmoothingBuffer.total_deposited_inr)).scalar() or 0
    total_released = db.query(func.sum(SmoothingBuffer.total_released_inr)).scalar() or 0
    
    print(f"Total Buffers: {total_buffers}")
    print(f"Total Buffer Balance: ₹{total_buffer_balance:,.2f}")
    print(f"Total Deposited: ₹{total_deposited:,.2f}")
    print(f"Total Released: ₹{total_released:,.2f}")
    print(f"Avg Buffer per User: ₹{total_buffer_balance/total_buffers:,.2f}")
    
    # Data Quality Checks
    print("\n✅ DATA QUALITY CHECKS")
    print("-" * 80)
    
    checks = []
    
    # Check 1: All users have transactions
    users_without_txns = total_users - db.query(func.count(func.distinct(Transaction.user_id))).scalar()
    checks.append(("Users without transactions", users_without_txns, users_without_txns == 0))
    
    # Check 2: All users have features
    users_without_features = total_users - users_with_features
    checks.append(("Users without features", users_without_features, users_without_features == 0))
    
    # Check 3: All users have predictions
    users_without_predictions = total_users - users_with_predictions
    checks.append(("Users without predictions", users_without_predictions, users_without_predictions == 0))
    
    # Check 4: All users have buffers
    users_without_buffers = total_users - total_buffers
    checks.append(("Users without buffers", users_without_buffers, users_without_buffers == 0))
    
    # Check 5: Transaction balance consistency
    negative_balances = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.balance_after_txn < 0
    ).scalar()
    checks.append(("Transactions with negative balance", negative_balances, negative_balances == 0))
    
    for check_name, count, passed in checks:
        status = "✅ PASS" if passed else "⚠️  WARN"
        print(f"{status} - {check_name}: {count}")
    
    # Sample Users
    print("\n👥 SAMPLE USERS (First 10)")
    print("-" * 80)
    
    sample_users = db.query(User).limit(10).all()
    for i, user in enumerate(sample_users, 1):
        user_txns = db.query(func.count(Transaction.transaction_id)).filter(
            Transaction.user_id == user.user_id
        ).scalar()
        print(f"{i}. {user.email}")
        print(f"   Name: {user.full_name}")
        print(f"   Transactions: {user_txns}")
        print(f"   Created: {user.created_at.strftime('%Y-%m-%d')}")
    
    # Database Size Estimate
    print("\n💾 DATABASE SIZE ESTIMATE")
    print("-" * 80)
    
    # Rough estimates (bytes per record)
    user_size = total_users * 500
    txn_size = total_transactions * 300
    feature_size = total_features * 400
    prediction_size = total_predictions * 300
    
    total_size = user_size + txn_size + feature_size + prediction_size
    
    print(f"Users: ~{user_size/1024/1024:.2f} MB")
    print(f"Transactions: ~{txn_size/1024/1024:.2f} MB")
    print(f"Features: ~{feature_size/1024/1024:.2f} MB")
    print(f"Predictions: ~{prediction_size/1024/1024:.2f} MB")
    print(f"Total Estimated: ~{total_size/1024/1024:.2f} MB")
    
    print("\n" + "=" * 80)
    print("✨ Validation Complete!")
    print("=" * 80)
    
    db.close()


if __name__ == "__main__":
    validate_and_report()
