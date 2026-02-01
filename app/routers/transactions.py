from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, Transaction, BankAccount
from app.schemas import TransactionResponse, TransactionCreate, BankAccountResponse, BankAccountCreate
from app.auth import get_current_active_user
from app.ml_service_enhanced import EnhancedMLService
from decimal import Decimal
import hashlib

router = APIRouter()


@router.post("/bank-accounts", response_model=BankAccountResponse)
def create_bank_account(
    account_data: BankAccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new bank account"""
    # Encrypt account number (simple hash for demo)
    encrypted_number = hashlib.sha256(account_data.account_number.encode()).hexdigest()
    
    # If this is primary, unset other primary accounts
    if account_data.is_primary:
        db.query(BankAccount).filter(
            BankAccount.user_id == current_user.user_id,
            BankAccount.is_primary == True
        ).update({"is_primary": False})
    
    account = BankAccount(
        user_id=current_user.user_id,
        account_number_encrypted=encrypted_number,
        bank_name=account_data.bank_name,
        account_type=account_data.account_type,
        is_primary=account_data.is_primary,
        current_balance_inr=Decimal('0')
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


@router.get("/bank-accounts", response_model=List[BankAccountResponse])
def get_bank_accounts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all bank accounts for current user"""
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.user_id
    ).all()
    
    return accounts


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    txn_data: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    # Verify account belongs to user
    account = db.query(BankAccount).filter(
        BankAccount.account_id == txn_data.account_id,
        BankAccount.user_id == current_user.user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Determine if income
    is_income = txn_data.txn_type.value == "credit"
    
    transaction = Transaction(
        user_id=current_user.user_id,
        account_id=txn_data.account_id,
        txn_timestamp=txn_data.txn_timestamp,
        amount_inr=txn_data.amount_inr,
        txn_type=txn_data.txn_type,
        balance_after_txn=txn_data.balance_after_txn,
        description=txn_data.description,
        merchant_category=txn_data.merchant_category,
        is_income=is_income
    )
    
    db.add(transaction)
    
    # Update account balance
    account.current_balance_inr = txn_data.balance_after_txn
    account.last_synced_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transactions for current user"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.user_id,
        Transaction.txn_timestamp >= cutoff_date
    ).order_by(Transaction.txn_timestamp.desc()).all()
    
    return transactions


@router.post("/sync")
def sync_transactions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger ML feature extraction and analysis using enhanced ML service"""
    ml_service = EnhancedMLService(db)
    
    # Extract features
    ml_service.extract_features(str(current_user.user_id))
    
    # Update income sources
    ml_service.update_income_sources(str(current_user.user_id))
    
    # Generate insights
    ml_service.generate_insights(str(current_user.user_id))
    
    return {
        "status": "success",
        "message": "Transactions synced and analyzed"
    }
