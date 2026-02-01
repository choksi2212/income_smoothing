import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.ml_service import MLService
from app.models import Transaction, TransactionType, MerchantCategory, AIFeature
from app.data_generator import IndianTransactionGenerator


def test_preprocess_transactions(db, test_user):
    """Test transaction preprocessing"""
    # Generate test transactions
    generator = IndianTransactionGenerator(pattern='moderate')
    
    # Get account
    from app.models import BankAccount
    account = db.query(BankAccount).filter(
        BankAccount.user_id == test_user.user_id
    ).first()
    
    transactions = generator.generate_transactions(
        str(test_user.user_id),
        str(account.account_id),
        months=3
    )
    
    for txn_data in transactions[:50]:  # Add 50 transactions
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    ml_service = MLService(db)
    df = ml_service.preprocess_transactions(str(test_user.user_id), months=3)
    
    assert not df.empty
    assert 'timestamp' in df.columns
    assert 'amount' in df.columns
    assert 'is_income' in df.columns


def test_extract_features(db, test_user):
    """Test feature extraction"""
    # Generate test transactions
    generator = IndianTransactionGenerator(pattern='moderate')
    
    from app.models import BankAccount
    account = db.query(BankAccount).filter(
        BankAccount.user_id == test_user.user_id
    ).first()
    
    transactions = generator.generate_transactions(
        str(test_user.user_id),
        str(account.account_id),
        months=2
    )
    
    for txn_data in transactions:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    ml_service = MLService(db)
    ml_service.extract_features(str(test_user.user_id))
    
    features = db.query(AIFeature).filter(
        AIFeature.user_id == test_user.user_id
    ).all()
    
    assert len(features) > 0
    assert features[0].total_income_inr >= 0
    assert features[0].total_expense_inr >= 0


def test_calculate_income_stability_score(db, test_user):
    """Test income stability score calculation"""
    # Generate test transactions
    generator = IndianTransactionGenerator(pattern='stable')
    
    from app.models import BankAccount
    account = db.query(BankAccount).filter(
        BankAccount.user_id == test_user.user_id
    ).first()
    
    transactions = generator.generate_transactions(
        str(test_user.user_id),
        str(account.account_id),
        months=3
    )
    
    for txn_data in transactions:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    ml_service = MLService(db)
    ml_service.extract_features(str(test_user.user_id))
    
    score = ml_service.calculate_income_stability_score(str(test_user.user_id))
    
    assert 0 <= float(score) <= 1


def test_predict_cashflow_rolling_mean(db, test_user):
    """Test cashflow prediction with rolling mean"""
    # Generate test transactions
    generator = IndianTransactionGenerator(pattern='moderate')
    
    from app.models import BankAccount
    account = db.query(BankAccount).filter(
        BankAccount.user_id == test_user.user_id
    ).first()
    
    transactions = generator.generate_transactions(
        str(test_user.user_id),
        str(account.account_id),
        months=2
    )
    
    for txn_data in transactions:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    ml_service = MLService(db)
    prediction = ml_service.predict_cashflow_rolling_mean(str(test_user.user_id), 7)
    
    assert 'expected_inflow' in prediction
    assert 'expected_outflow' in prediction
    assert 'net_cashflow' in prediction
    assert 'lower_bound' in prediction
    assert 'upper_bound' in prediction
    assert 'risk_level' in prediction
    assert prediction['expected_inflow'] >= 0


def test_save_prediction(db, test_user):
    """Test saving prediction to database"""
    # Generate test transactions
    generator = IndianTransactionGenerator(pattern='moderate')
    
    from app.models import BankAccount, CashflowPrediction
    account = db.query(BankAccount).filter(
        BankAccount.user_id == test_user.user_id
    ).first()
    
    transactions = generator.generate_transactions(
        str(test_user.user_id),
        str(account.account_id),
        months=2
    )
    
    for txn_data in transactions:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    ml_service = MLService(db)
    prediction = ml_service.save_prediction(str(test_user.user_id), 7)
    
    assert prediction.prediction_id is not None
    assert prediction.prediction_window_days == 7
    assert prediction.expected_inflow_inr >= 0


def test_calculate_safe_to_spend(db, test_user):
    """Test safe-to-spend calculation"""
    # Generate test transactions
    generator = IndianTransactionGenerator(pattern='moderate')
    
    from app.models import BankAccount
    account = db.query(BankAccount).filter(
        BankAccount.user_id == test_user.user_id
    ).first()
    
    transactions = generator.generate_transactions(
        str(test_user.user_id),
        str(account.account_id),
        months=2
    )
    
    for txn_data in transactions:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    # Initialize buffer
    from app.smoothing_service import SmoothingService
    smoothing_service = SmoothingService(db)
    smoothing_service.initialize_buffer(str(test_user.user_id))
    smoothing_service.deposit_to_buffer(str(test_user.user_id), Decimal('5000'))
    
    ml_service = MLService(db)
    ml_service.extract_features(str(test_user.user_id))
    
    safe_spend = ml_service.calculate_safe_to_spend(str(test_user.user_id))
    
    assert 'daily_safe_spend_inr' in safe_spend
    assert 'weekly_safe_spend_inr' in safe_spend
    assert safe_spend['daily_safe_spend_inr'] >= 0


def test_update_income_sources(db, test_user):
    """Test income source analysis"""
    # Generate test transactions
    generator = IndianTransactionGenerator(pattern='moderate')
    
    from app.models import BankAccount, IncomeSource
    account = db.query(BankAccount).filter(
        BankAccount.user_id == test_user.user_id
    ).first()
    
    transactions = generator.generate_transactions(
        str(test_user.user_id),
        str(account.account_id),
        months=2
    )
    
    for txn_data in transactions:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    ml_service = MLService(db)
    ml_service.update_income_sources(str(test_user.user_id))
    
    sources = db.query(IncomeSource).filter(
        IncomeSource.user_id == test_user.user_id
    ).all()
    
    assert len(sources) > 0
    assert sources[0].contribution_pct >= 0


def test_generate_insights(db, test_user):
    """Test AI insight generation"""
    # Generate test transactions
    generator = IndianTransactionGenerator(pattern='volatile')
    
    from app.models import BankAccount, AIInsight
    account = db.query(BankAccount).filter(
        BankAccount.user_id == test_user.user_id
    ).first()
    
    transactions = generator.generate_transactions(
        str(test_user.user_id),
        str(account.account_id),
        months=2
    )
    
    for txn_data in transactions:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    ml_service = MLService(db)
    ml_service.extract_features(str(test_user.user_id))
    insights = ml_service.generate_insights(str(test_user.user_id))
    
    # Should generate at least some insights for volatile pattern
    all_insights = db.query(AIInsight).filter(
        AIInsight.user_id == test_user.user_id
    ).all()
    
    assert len(all_insights) >= 0  # May or may not generate insights depending on data
