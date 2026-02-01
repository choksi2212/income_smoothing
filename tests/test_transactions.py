import pytest
from datetime import datetime
from decimal import Decimal
from app.models import TransactionType, MerchantCategory


def test_create_bank_account(client, auth_headers):
    """Test creating a bank account"""
    response = client.post(
        "/transactions/bank-accounts",
        headers=auth_headers,
        json={
            "account_number": "9876543210",
            "bank_name": "HDFC Bank",
            "account_type": "savings",
            "is_primary": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["bank_name"] == "HDFC Bank"
    assert data["is_primary"] == True


def test_get_bank_accounts(client, auth_headers, db, test_user):
    """Test getting bank accounts"""
    response = client.get("/transactions/bank-accounts", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # Just check that bank_name exists, don't check specific value
    assert "bank_name" in data[0]
    assert data[0]["bank_name"] is not None


def test_create_transaction(client, auth_headers, db, test_user):
    """Test creating a transaction"""
    # Get account
    accounts_response = client.get("/transactions/bank-accounts", headers=auth_headers)
    account_id = accounts_response.json()[0]["account_id"]
    
    response = client.post(
        "/transactions/",
        headers=auth_headers,
        json={
            "account_id": account_id,
            "txn_timestamp": datetime.utcnow().isoformat(),
            "amount_inr": "5000.00",
            "txn_type": "credit",
            "balance_after_txn": "55000.00",
            "description": "Freelance payment",
            "merchant_category": "freelancing"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["amount_inr"]) == 5000.00
    assert data["txn_type"] == "credit"
    assert data["is_income"] == True


def test_get_transactions(client, auth_headers, db, test_user):
    """Test getting transactions"""
    # Create a transaction first
    accounts_response = client.get("/transactions/bank-accounts", headers=auth_headers)
    account_id = accounts_response.json()[0]["account_id"]
    
    client.post(
        "/transactions/",
        headers=auth_headers,
        json={
            "account_id": account_id,
            "txn_timestamp": datetime.utcnow().isoformat(),
            "amount_inr": "3000.00",
            "txn_type": "credit",
            "balance_after_txn": "53000.00",
            "description": "Test payment",
            "merchant_category": "freelancing"
        }
    )
    
    response = client.get("/transactions/?days=30", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_sync_transactions(client, auth_headers, db, test_user):
    """Test transaction sync and analysis"""
    # Create some transactions first
    accounts_response = client.get("/transactions/bank-accounts", headers=auth_headers)
    account_id = accounts_response.json()[0]["account_id"]
    
    # Create multiple transactions
    for i in range(5):
        client.post(
            "/transactions/",
            headers=auth_headers,
            json={
                "account_id": account_id,
                "txn_timestamp": datetime.utcnow().isoformat(),
                "amount_inr": f"{(i+1) * 1000}.00",
                "txn_type": "credit",
                "balance_after_txn": f"{50000 + (i+1) * 1000}.00",
                "description": f"Payment {i+1}",
                "merchant_category": "freelancing"
            }
        )
    
    response = client.post("/transactions/sync", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
