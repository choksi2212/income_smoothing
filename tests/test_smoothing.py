import pytest
from decimal import Decimal
from app.smoothing_service import SmoothingService
from app.models import SmoothingBuffer, WeeklyRelease
from app.data_generator import IndianTransactionGenerator
from app.models import Transaction


def test_initialize_buffer(db, test_user):
    """Test buffer initialization"""
    smoothing_service = SmoothingService(db)
    
    # Delete existing buffer if any
    existing_buffer = db.query(SmoothingBuffer).filter(
        SmoothingBuffer.user_id == test_user.user_id
    ).first()
    if existing_buffer:
        db.delete(existing_buffer)
        db.commit()
    
    buffer = smoothing_service.initialize_buffer(str(test_user.user_id))
    
    assert buffer.buffer_balance_inr == Decimal('0')
    assert buffer.min_buffer_threshold_inr == Decimal('5000')
    assert buffer.max_buffer_capacity_inr == Decimal('100000')


def test_deposit_to_buffer(db, test_user):
    """Test depositing to buffer"""
    smoothing_service = SmoothingService(db)
    
    # Delete existing buffer if any
    existing_buffer = db.query(SmoothingBuffer).filter(
        SmoothingBuffer.user_id == test_user.user_id
    ).first()
    if existing_buffer:
        db.delete(existing_buffer)
        db.commit()
    
    buffer = smoothing_service.initialize_buffer(str(test_user.user_id))
    
    updated_buffer = smoothing_service.deposit_to_buffer(
        str(test_user.user_id),
        Decimal('10000')
    )
    
    assert updated_buffer.buffer_balance_inr == Decimal('10000')
    assert updated_buffer.total_deposited_inr == Decimal('10000')


def test_deposit_exceeds_capacity(db, test_user):
    """Test deposit that exceeds capacity"""
    smoothing_service = SmoothingService(db)
    buffer = smoothing_service.initialize_buffer(str(test_user.user_id))
    
    # Try to deposit more than capacity
    updated_buffer = smoothing_service.deposit_to_buffer(
        str(test_user.user_id),
        Decimal('150000')
    )
    
    # Should cap at max capacity
    assert updated_buffer.buffer_balance_inr == buffer.max_buffer_capacity_inr


def test_calculate_weekly_release(db, test_user):
    """Test weekly release calculation"""
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
    
    # Extract features
    from app.ml_service import MLService
    ml_service = MLService(db)
    ml_service.extract_features(str(test_user.user_id))
    
    # Initialize buffer with some balance
    smoothing_service = SmoothingService(db)
    smoothing_service.initialize_buffer(str(test_user.user_id))
    smoothing_service.deposit_to_buffer(str(test_user.user_id), Decimal('15000'))
    
    release_calc = smoothing_service.calculate_weekly_release(str(test_user.user_id))
    
    assert 'recommended_weekly_release_inr' in release_calc
    assert 'buffer_balance_inr' in release_calc
    assert 'buffer_risk_score' in release_calc
    assert release_calc['recommended_weekly_release_inr'] >= 0


def test_create_weekly_release(db, test_user):
    """Test creating weekly release record"""
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
    
    # Extract features
    from app.ml_service import MLService
    ml_service = MLService(db)
    ml_service.extract_features(str(test_user.user_id))
    
    # Clean up old releases
    db.query(WeeklyRelease).filter(WeeklyRelease.user_id == test_user.user_id).delete()
    db.commit()
    
    # Initialize buffer
    smoothing_service = SmoothingService(db)
    
    # Delete existing buffer if any
    existing_buffer = db.query(SmoothingBuffer).filter(
        SmoothingBuffer.user_id == test_user.user_id
    ).first()
    if existing_buffer:
        db.delete(existing_buffer)
        db.commit()
    
    smoothing_service.initialize_buffer(str(test_user.user_id))
    smoothing_service.deposit_to_buffer(str(test_user.user_id), Decimal('10000'))
    
    release = smoothing_service.create_weekly_release(str(test_user.user_id))
    
    assert release.release_id is not None
    assert release.recommended_weekly_release_inr >= 0
    assert release.is_released == False


def test_execute_weekly_release(db, test_user):
    """Test executing weekly release"""
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
    
    # Extract features
    from app.ml_service import MLService
    ml_service = MLService(db)
    ml_service.extract_features(str(test_user.user_id))
    
    # Clean up old releases
    db.query(WeeklyRelease).filter(WeeklyRelease.user_id == test_user.user_id).delete()
    db.commit()
    
    # Initialize buffer
    smoothing_service = SmoothingService(db)
    
    # Delete existing buffer if any
    existing_buffer = db.query(SmoothingBuffer).filter(
        SmoothingBuffer.user_id == test_user.user_id
    ).first()
    if existing_buffer:
        db.delete(existing_buffer)
        db.commit()
    
    smoothing_service.initialize_buffer(str(test_user.user_id))
    smoothing_service.deposit_to_buffer(str(test_user.user_id), Decimal('10000'))
    
    # Create release
    release = smoothing_service.create_weekly_release(str(test_user.user_id))
    
    # Execute release
    executed_release = smoothing_service.execute_weekly_release(
        str(test_user.user_id),
        str(release.release_id)
    )
    
    assert executed_release.is_released == True
    assert executed_release.actual_release_inr > 0
    assert executed_release.released_at is not None


def test_process_income_smoothing(db, test_user):
    """Test income smoothing process"""
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
    
    # Extract features
    from app.ml_service import MLService
    ml_service = MLService(db)
    ml_service.extract_features(str(test_user.user_id))
    
    # Initialize buffer
    smoothing_service = SmoothingService(db)
    smoothing_service.initialize_buffer(str(test_user.user_id))
    
    result = smoothing_service.process_income_smoothing(str(test_user.user_id))
    
    assert 'status' in result
    assert result['status'] in ['excess_deposited', 'deficit_covered', 'deficit_warning', 'normal', 'insufficient_data']
