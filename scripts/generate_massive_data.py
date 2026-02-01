import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, UserProfile, BankAccount, Transaction
from app.auth import get_password_hash
from app.data_generator import IndianTransactionGenerator
from app.ml_service import MLService
from app.smoothing_service import SmoothingService
from decimal import Decimal
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from datetime import datetime

# Configuration
NUM_USERS = 100  # Number of users to generate
MIN_MONTHS = 12  # Minimum months of data
MAX_MONTHS = 24  # Maximum months of data
BATCH_SIZE = 10  # Process users in batches
MAX_WORKERS = 4  # Parallel processing threads


def generate_user_profile():
    """Generate realistic user profile data"""
    occupations = [
        'Freelance Developer', 'Graphic Designer', 'Content Writer', 
        'Video Editor', 'Digital Marketer', 'Consultant', 'Tutor',
        'Photographer', 'Web Developer', 'UI/UX Designer', 'Data Analyst',
        'Social Media Manager', 'Translator', 'Voice Artist', 'Animator'
    ]
    
    cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 
        'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow'
    ]
    
    patterns = ['stable', 'moderate', 'volatile', 'seasonal', 'growing', 'declining']
    
    first_names = [
        'Rahul', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anjali', 'Rohan', 'Neha',
        'Arjun', 'Pooja', 'Karan', 'Divya', 'Aditya', 'Riya', 'Sanjay', 'Kavya',
        'Rajesh', 'Meera', 'Nikhil', 'Shreya', 'Varun', 'Ananya', 'Manish', 'Isha'
    ]
    
    last_names = [
        'Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Gupta', 'Verma', 'Joshi',
        'Mehta', 'Nair', 'Iyer', 'Desai', 'Rao', 'Pillai', 'Agarwal', 'Malhotra'
    ]
    
    user_num = random.randint(1000, 9999)
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    city = random.choice(cities)
    occupation = random.choice(occupations)
    pattern = random.choice(patterns)
    months = random.randint(MIN_MONTHS, MAX_MONTHS)
    
    # Generate realistic expenses based on city
    city_expense_multiplier = {
        'Mumbai': 1.5, 'Delhi': 1.4, 'Bangalore': 1.4, 'Hyderabad': 1.2,
        'Chennai': 1.2, 'Pune': 1.3, 'Kolkata': 1.1, 'Ahmedabad': 1.1,
        'Jaipur': 1.0, 'Lucknow': 0.9
    }
    
    base_expense = 10000
    monthly_expense = int(base_expense * city_expense_multiplier.get(city, 1.0))
    
    return {
        'email': f'{first_name.lower()}.{last_name.lower()}{user_num}@example.com',
        'full_name': f'{first_name} {last_name}',
        'phone': f'+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}',
        'password': 'SecurePass123',
        'occupation': occupation,
        'city': city,
        'pattern': pattern,
        'months': months,
        'monthly_fixed_expenses': monthly_expense
    }


def create_user_with_data(user_data, user_index, total_users):
    """Create a single user with all their data"""
    db = SessionLocal()
    
    try:
        print(f"\n[{user_index + 1}/{total_users}] Creating user: {user_data['email']}")
        print(f"  Pattern: {user_data['pattern']}, Months: {user_data['months']}, City: {user_data['city']}")
        
        # Check if user exists
        existing = db.query(User).filter(User.email == user_data['email']).first()
        if existing:
            print(f"  ⚠️  User already exists, skipping...")
            db.close()
            return False
        
        # Create user
        user = User(
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
            primary_income_type='Freelancing',
            monthly_fixed_expenses_inr=Decimal(str(user_data['monthly_fixed_expenses'])),
            risk_tolerance='conservative'
        )
        db.add(profile)
        
        # Create bank account
        account_number = f"{random.randint(1000000000, 9999999999)}"
        encrypted_number = hashlib.sha256(account_number.encode()).hexdigest()
        
        account = BankAccount(
            user_id=user.user_id,
            account_number_encrypted=encrypted_number,
            bank_name=random.choice(['HDFC Bank', 'ICICI Bank', 'SBI', 'Axis Bank', 'Kotak Mahindra']),
            account_type='savings',
            is_primary=True,
            current_balance_inr=Decimal(str(random.randint(20000, 100000)))
        )
        db.add(account)
        db.flush()
        
        # Generate transactions
        print(f"  📊 Generating {user_data['months']} months of transactions...")
        generator = IndianTransactionGenerator(pattern=user_data['pattern'])
        transactions = generator.generate_transactions(
            str(user.user_id),
            str(account.account_id),
            months=user_data['months']
        )
        
        print(f"  💾 Saving {len(transactions)} transactions...")
        
        # Batch insert transactions for performance
        batch_size = 500
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            for txn_data in batch:
                txn = Transaction(**txn_data)
                db.add(txn)
            db.flush()
            print(f"    Saved {min(i + batch_size, len(transactions))}/{len(transactions)} transactions")
        
        # Update account balance
        if transactions:
            account.current_balance_inr = transactions[-1]['balance_after_txn']
        
        db.commit()
        
        # Run ML analysis
        print(f"  🧠 Running ML analysis...")
        ml_service = MLService(db)
        ml_service.extract_features(str(user.user_id))
        ml_service.update_income_sources(str(user.user_id))
        
        # Generate predictions
        for days in [7, 30, 60]:
            ml_service.save_prediction(str(user.user_id), days)
        
        ml_service.generate_insights(str(user.user_id))
        
        # Initialize smoothing
        smoothing_service = SmoothingService(db)
        buffer = smoothing_service.initialize_buffer(str(user.user_id))
        
        # Simulate buffer deposits based on pattern
        if user_data['pattern'] in ['stable', 'growing']:
            deposit_amount = Decimal(str(random.randint(15000, 30000)))
        elif user_data['pattern'] == 'moderate':
            deposit_amount = Decimal(str(random.randint(8000, 15000)))
        else:
            deposit_amount = Decimal(str(random.randint(3000, 8000)))
        
        smoothing_service.deposit_to_buffer(str(user.user_id), deposit_amount)
        smoothing_service.create_weekly_release(str(user.user_id))
        
        print(f"  ✅ User created successfully!")
        print(f"     Transactions: {len(transactions)}")
        print(f"     Buffer: ₹{deposit_amount}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating user: {e}")
        db.rollback()
        db.close()
        return False


def generate_massive_dataset():
    """Generate massive dataset with parallel processing"""
    print("=" * 80)
    print("MASSIVE DATA GENERATION")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Users to generate: {NUM_USERS}")
    print(f"  Data range: {MIN_MONTHS}-{MAX_MONTHS} months per user")
    print(f"  Parallel workers: {MAX_WORKERS}")
    print(f"  Batch size: {BATCH_SIZE}")
    print("\n" + "=" * 80)
    
    start_time = datetime.now()
    
    # Generate user profiles
    print(f"\n📋 Generating {NUM_USERS} user profiles...")
    user_profiles = [generate_user_profile() for _ in range(NUM_USERS)]
    
    # Process users in parallel
    print(f"\n🚀 Starting parallel data generation with {MAX_WORKERS} workers...")
    
    successful = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        futures = {
            executor.submit(create_user_with_data, profile, idx, NUM_USERS): idx 
            for idx, profile in enumerate(user_profiles)
        }
        
        # Process completed tasks
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Task failed with error: {e}")
                failed += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Summary
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Statistics:")
    print(f"  Total users attempted: {NUM_USERS}")
    print(f"  Successfully created: {successful}")
    print(f"  Failed/Skipped: {failed}")
    print(f"  Success rate: {(successful/NUM_USERS*100):.1f}%")
    print(f"\n⏱️  Time taken: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"  Average time per user: {duration/NUM_USERS:.2f} seconds")
    
    # Estimate total data
    avg_transactions = (MIN_MONTHS + MAX_MONTHS) / 2 * 30 * 3  # ~3 transactions per day
    total_transactions = successful * avg_transactions
    
    print(f"\n💾 Estimated data generated:")
    print(f"  Total transactions: ~{int(total_transactions):,}")
    print(f"  Total features: ~{successful * 52}")  # ~52 weeks per year
    print(f"  Total predictions: {successful * 3}")  # 3 predictions per user
    print(f"  Total insights: ~{successful * 2}")  # ~2 insights per user
    
    print("\n" + "=" * 80)
    print("✨ Massive dataset generation complete!")
    print("=" * 80)
    
    # Print sample credentials
    print("\n🔐 Sample Test Credentials:")
    print("-" * 80)
    for i, profile in enumerate(user_profiles[:5]):
        print(f"{i+1}. Email: {profile['email']}")
        print(f"   Password: {profile['password']}")
        print(f"   Pattern: {profile['pattern']}, City: {profile['city']}")
        print()


if __name__ == "__main__":
    try:
        generate_massive_dataset()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        raise
