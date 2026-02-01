"""
Manual Data Entry Router
Allows users to manually add transactions, income sources, and other data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.database import get_db
from app.models import User, Transaction, BankAccount, IncomeSource, TransactionType
from app.schemas import (
    TransactionResponse, 
    TransactionCreate,
    BankAccountResponse,
    BankAccountCreate,
    IncomeSourceResponse
)
from app.auth import get_current_active_user
from app.ml_service_enhanced import EnhancedMLService
import hashlib
import uuid

router = APIRouter()


@router.post("/transactions", response_model=TransactionResponse)
def create_manual_transaction(
    txn_data: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Manually create a transaction
    Users can add income or expense transactions manually
    """
    # Verify account belongs to user
    account = db.query(BankAccount).filter(
        BankAccount.account_id == txn_data.account_id,
        BankAccount.user_id == current_user.user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Determine if income based on transaction type
    is_income = txn_data.txn_type == TransactionType.CREDIT
    
    # Create transaction
    transaction = Transaction(
        user_id=current_user.user_id,
        account_id=txn_data.account_id,
        txn_timestamp=txn_data.txn_timestamp or datetime.utcnow(),
        amount_inr=txn_data.amount_inr,
        txn_type=txn_data.txn_type,
        balance_after_txn=txn_data.balance_after_txn,
        description=txn_data.description or "Manual entry",
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


@router.post("/transactions/bulk", response_model=List[TransactionResponse])
def create_bulk_transactions(
    transactions: List[TransactionCreate],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create multiple transactions at once
    Useful for importing data from spreadsheets
    """
    created_transactions = []
    
    for txn_data in transactions:
        # Verify account belongs to user
        account = db.query(BankAccount).filter(
            BankAccount.account_id == txn_data.account_id,
            BankAccount.user_id == current_user.user_id
        ).first()
        
        if not account:
            continue  # Skip invalid accounts
        
        # Determine if income
        is_income = txn_data.txn_type == TransactionType.CREDIT
        
        # Create transaction
        transaction = Transaction(
            user_id=current_user.user_id,
            account_id=txn_data.account_id,
            txn_timestamp=txn_data.txn_timestamp or datetime.utcnow(),
            amount_inr=txn_data.amount_inr,
            txn_type=txn_data.txn_type,
            balance_after_txn=txn_data.balance_after_txn,
            description=txn_data.description or "Manual entry",
            merchant_category=txn_data.merchant_category,
            is_income=is_income
        )
        
        db.add(transaction)
        created_transactions.append(transaction)
        
        # Update account balance
        account.current_balance_inr = txn_data.balance_after_txn
        account.last_synced_at = datetime.utcnow()
    
    db.commit()
    
    for txn in created_transactions:
        db.refresh(txn)
    
    return created_transactions


@router.post("/bank-accounts", response_model=BankAccountResponse)
def create_manual_bank_account(
    account_data: BankAccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Manually add a bank account
    Users can add their bank accounts for tracking
    """
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


@router.post("/income-sources", response_model=IncomeSourceResponse)
def create_manual_income_source(
    source_name: str,
    source_category: str,
    avg_monthly_inr: Decimal,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Manually add an income source
    Users can define their income sources manually
    """
    # Check if source already exists
    existing = db.query(IncomeSource).filter(
        IncomeSource.user_id == current_user.user_id,
        IncomeSource.source_name == source_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Income source already exists")
    
    # Calculate contribution percentage (will be updated when ML runs)
    total_income = db.query(Transaction).filter(
        Transaction.user_id == current_user.user_id,
        Transaction.is_income == True
    ).count()
    
    contribution_pct = Decimal('100.0') if total_income == 0 else Decimal('0.0')
    
    income_source = IncomeSource(
        user_id=current_user.user_id,
        source_name=source_name,
        source_category=source_category,
        avg_monthly_inr=avg_monthly_inr,
        contribution_pct=contribution_pct,
        stability_score=Decimal('0.5'),  # Default medium stability
        last_payment_date=None
    )
    
    db.add(income_source)
    db.commit()
    db.refresh(income_source)
    
    return income_source


@router.post("/analyze")
def analyze_manual_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Trigger ML analysis on manually entered data
    Extracts features, updates income sources, generates insights
    """
    ml_service = EnhancedMLService(db)
    user_id = str(current_user.user_id)
    
    try:
        # Extract features
        ml_service.extract_features(user_id)
        
        # Update income sources
        ml_service.update_income_sources(user_id)
        
        # Generate insights
        insights = ml_service.generate_insights(user_id)
        
        # Generate predictions
        predictions = []
        for days in [7, 30, 60]:
            pred = ml_service.save_prediction(user_id, days)
            predictions.append(pred)
        
        return {
            "status": "success",
            "message": "Data analyzed successfully",
            "insights_generated": len(insights),
            "predictions_generated": len(predictions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/template/csv")
def get_csv_template():
    """
    Get CSV template for bulk transaction import
    Returns CSV format that users can fill and upload
    """
    template = """date,type,amount,description,category,balance_after
2026-02-01,credit,50000,Freelance payment,freelancing,50000
2026-02-02,debit,500,Grocery shopping,groceries,49500
2026-02-03,credit,25000,Consulting fee,consulting,74500
2026-02-04,debit,1200,Restaurant,food,73300"""
    
    return {
        "template": template,
        "instructions": {
            "date": "Format: YYYY-MM-DD",
            "type": "credit (income) or debit (expense)",
            "amount": "Amount in INR (without commas)",
            "description": "Transaction description",
            "category": "Category (freelancing, groceries, food, etc.)",
            "balance_after": "Account balance after transaction"
        }
    }


@router.delete("/transactions/{transaction_id}")
def delete_manual_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a manually entered transaction
    """
    transaction = db.query(Transaction).filter(
        Transaction.txn_id == transaction_id,
        Transaction.user_id == current_user.user_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    
    return {"status": "success", "message": "Transaction deleted"}


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_manual_transaction(
    transaction_id: str,
    txn_data: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a manually entered transaction
    """
    transaction = db.query(Transaction).filter(
        Transaction.txn_id == transaction_id,
        Transaction.user_id == current_user.user_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update fields
    transaction.txn_timestamp = txn_data.txn_timestamp or transaction.txn_timestamp
    transaction.amount_inr = txn_data.amount_inr
    transaction.txn_type = txn_data.txn_type
    transaction.balance_after_txn = txn_data.balance_after_txn
    transaction.description = txn_data.description or transaction.description
    transaction.merchant_category = txn_data.merchant_category
    transaction.is_income = txn_data.txn_type == TransactionType.CREDIT
    
    db.commit()
    db.refresh(transaction)
    
    return transaction
