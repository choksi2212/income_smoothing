import pytest
from datetime import datetime
from app.data_generator import IndianTransactionGenerator
from app.models import Transaction


def test_get_buffer(client, auth_headers):
    """Test getting smoothing buffer"""
    response = client.get("/smoothing/buffer", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "buffer_balance_inr" in data
    assert "buffer_risk_score" in data


def test_get_predictions(client, auth_headers, db, test_user):
    """Test getting predictions"""
    # Generate test data
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
    
    for txn_data in transactions[:100]:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    # Generate predictions
    response = client.post("/predictions/generate", headers=auth_headers)
    assert response.status_code == 200
    
    # Get predictions
    response = client.get("/predictions/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_safe_to_spend(client, auth_headers, db, test_user):
    """Test safe-to-spend endpoint"""
    # Generate test data
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
    
    for txn_data in transactions[:100]:
        txn = Transaction(**txn_data)
        db.add(txn)
    db.commit()
    
    # Sync transactions
    client.post("/transactions/sync", headers=auth_headers)
    
    # Get safe to spend
    response = client.get("/predictions/safe-to-spend", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "daily_safe_spend_inr" in data
    assert "weekly_safe_spend_inr" in data


def test_get_features(client, auth_headers, db, test_user):
    """Test getting AI features"""
    # Generate test data
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
    
    # Sync transactions
    client.post("/transactions/sync", headers=auth_headers)
    
    # Get features
    response = client.get("/features/?weeks=12", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_income_sources(client, auth_headers, db, test_user):
    """Test getting income sources"""
    # Generate test data
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
    
    # Sync transactions
    client.post("/transactions/sync", headers=auth_headers)
    
    # Get income sources
    response = client.get("/features/income-sources", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_insights(client, auth_headers, db, test_user):
    """Test getting AI insights"""
    # Generate test data
    generator = IndianTransactionGenerator(pattern='volatile')
    
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
    
    # Sync transactions
    client.post("/transactions/sync", headers=auth_headers)
    
    # Get insights
    response = client.get("/insights/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_generate_insights(client, auth_headers, db, test_user):
    """Test generating insights"""
    # Generate test data
    generator = IndianTransactionGenerator(pattern='volatile')
    
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
    
    # Sync transactions
    client.post("/transactions/sync", headers=auth_headers)
    
    # Generate insights
    response = client.post("/insights/generate", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_get_stability_score(client, auth_headers, db, test_user):
    """Test getting stability score"""
    # Generate test data
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
    
    # Sync transactions
    client.post("/transactions/sync", headers=auth_headers)
    
    # Get stability score
    response = client.get("/insights/stability-score", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "stability_score" in data
    assert 0 <= data["stability_score"] <= 1
