import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, UserProfile, BankAccount, Transaction
from app.auth import get_password_hash
from app.data_generator import IndianTransactionGenerator, generate_test_users
from app.ml_service import MLService
from app.smoothing_service import SmoothingService
from decimal import Decimal
import hashlib


def generate_test_data():
    """Generate complete test dataset"""
    db = SessionLocal()
    
    try:
        print("Generating test users and data...")
        
        test_users = generate_test_users(3)
        
        for user_data in test_users:
            print(f"\nCreating user: {user_data['email']}")
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data['email']).first()
            if existing_user:
                print(f"  User {user_data['email']} already exists, skipping...")
                continue
            
            # Create user
            user = User(
                user_id=user_data['user_id'],
                email=user_data['email'],
                hashed_password=get_password_hash(user_data['password']),
                full_name=user_data['full_name'],
                phone=user_data['phone']
            )
            db.add(user)
            db.flush()
            
            # Create profile
            profile = UserProfile(
                user_id=user.user_id,
                occupation=user_data['occupation'],
                primary_income_type="Freelancing",
                monthly_fixed_expenses_inr=Decimal(str(user_data['monthly_fixed_expenses'])),
                risk_tolerance="conservative"
            )
            db.add(profile)
            
            # Create bank account
            account_number = f"1234567890{user_data['email'][-2:]}"
            encrypted_number = hashlib.sha256(account_number.encode()).hexdigest()
            
            account = BankAccount(
                user_id=user.user_id,
                account_number_encrypted=encrypted_number,
                bank_name="HDFC Bank",
                account_type="savings",
                is_primary=True,
                current_balance_inr=Decimal('50000')
            )
            db.add(account)
            db.flush()
            
            # Generate transactions
            print(f"  Generating 6 months of transactions...")
            generator = IndianTransactionGenerator(pattern=user_data['pattern'])
            transactions = generator.generate_transactions(
                str(user.user_id),
                str(account.account_id),
                months=6
            )
            
            print(f"  Generated {len(transactions)} transactions")
            
            for txn_data in transactions:
                txn = Transaction(**txn_data)
                db.add(txn)
            
            # Update account balance
            if transactions:
                account.current_balance_inr = transactions[-1]['balance_after_txn']
            
            db.commit()
            
            # Run ML analysis
            print(f"  Extracting features...")
            ml_service = MLService(db)
            ml_service.extract_features(str(user.user_id))
            
            print(f"  Updating income sources...")
            ml_service.update_income_sources(str(user.user_id))
            
            print(f"  Generating predictions...")
            for days in [7, 30, 60]:
                ml_service.save_prediction(str(user.user_id), days)
            
            print(f"  Generating insights...")
            ml_service.generate_insights(str(user.user_id))
            
            # Initialize smoothing
            print(f"  Initializing income smoothing...")
            smoothing_service = SmoothingService(db)
            buffer = smoothing_service.initialize_buffer(str(user.user_id))
            
            # Simulate some buffer deposits
            smoothing_service.deposit_to_buffer(str(user.user_id), Decimal('10000'))
            
            # Create weekly releases
            smoothing_service.create_weekly_release(str(user.user_id))
            
            print(f"✓ User {user_data['email']} created successfully")
        
        print("\n✓ Test data generation complete!")
        print("\nTest user credentials:")
        print("=" * 50)
        for user_data in test_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Pattern: {user_data['pattern']}")
            print("-" * 50)
        
    except Exception as e:
        print(f"Error generating test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_test_data()
