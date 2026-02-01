"""Clean up test user for testing"""
from app.database import SessionLocal
from app.models import User, BankAccount, Transaction, SmoothingBuffer, WeeklyRelease, AIFeature, CashflowPrediction, AIInsight, IncomeSource, UserProfile
from sqlalchemy import delete

db = SessionLocal()

# Delete test user and all related records
user = db.query(User).filter(User.email == "test@example.com").first()
if user:
    user_id = user.user_id
    
    # Delete all related records
    db.query(WeeklyRelease).filter(WeeklyRelease.user_id == user_id).delete()
    db.query(AIInsight).filter(AIInsight.user_id == user_id).delete()
    db.query(IncomeSource).filter(IncomeSource.user_id == user_id).delete()
    db.query(CashflowPrediction).filter(CashflowPrediction.user_id == user_id).delete()
    db.query(AIFeature).filter(AIFeature.user_id == user_id).delete()
    db.query(SmoothingBuffer).filter(SmoothingBuffer.user_id == user_id).delete()
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.query(BankAccount).filter(BankAccount.user_id == user_id).delete()
    db.query(UserProfile).filter(UserProfile.user_id == user_id).delete()
    
    # Finally delete the user
    db.delete(user)
    db.commit()
    print("✅ Deleted existing test user and all related records")
else:
    print("ℹ️  No test user found")

db.close()
