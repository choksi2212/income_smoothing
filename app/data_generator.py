import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict
import uuid
from app.models import TransactionType, MerchantCategory
import pytz

IST = pytz.timezone('Asia/Kolkata')


class IndianTransactionGenerator:
    """Generate realistic Indian transaction data for testing"""
    
    # Indian-specific transaction descriptions
    INCOME_DESCRIPTIONS = {
        MerchantCategory.FREELANCING: [
            "Upwork payment received",
            "Fiverr gig payment",
            "Freelance project payment",
            "Client payment - web development",
            "Design project payment",
            "Content writing payment",
            "Consulting fee received"
        ],
        MerchantCategory.PLATFORM_PAYOUT: [
            "YouTube AdSense payout",
            "Swiggy weekly settlement",
            "Zomato earnings",
            "Uber driver payment",
            "Ola earnings",
            "Amazon seller payment",
            "Flipkart seller settlement"
        ],
        MerchantCategory.UPI_CREDIT: [
            "UPI payment from client",
            "Google Pay received",
            "PhonePe payment",
            "Paytm received",
            "BHIM UPI credit",
            "Payment received via UPI"
        ]
    }
    
    EXPENSE_DESCRIPTIONS = {
        MerchantCategory.RENT: [
            "Monthly rent payment",
            "House rent",
            "PG accommodation"
        ],
        MerchantCategory.FOOD_DELIVERY: [
            "Swiggy order",
            "Zomato food delivery",
            "Dunzo delivery",
            "Blinkit grocery",
            "BigBasket order"
        ],
        MerchantCategory.MOBILE_RECHARGE: [
            "Jio recharge",
            "Airtel prepaid",
            "Vi recharge",
            "BSNL recharge",
            "DTH recharge"
        ],
        MerchantCategory.TRAVEL: [
            "Uber ride",
            "Ola cab",
            "Rapido bike",
            "Metro card recharge",
            "Bus ticket",
            "Train ticket IRCTC",
            "Petrol pump"
        ],
        MerchantCategory.UTILITIES: [
            "Electricity bill",
            "Water bill",
            "Gas cylinder",
            "Broadband bill",
            "Mobile postpaid"
        ],
        MerchantCategory.SHOPPING: [
            "Amazon purchase",
            "Flipkart order",
            "Myntra shopping",
            "DMart",
            "Reliance Digital",
            "Local kirana store"
        ],
        MerchantCategory.ENTERTAINMENT: [
            "Netflix subscription",
            "Amazon Prime",
            "Hotstar subscription",
            "Spotify premium",
            "BookMyShow tickets",
            "PVR cinema"
        ]
    }
    
    # Income patterns for different freelancer types
    INCOME_PATTERNS = {
        'stable': {
            'weekly_base': 15000,
            'volatility': 0.2,
            'frequency': 0.7  # 70% of days have income
        },
        'moderate': {
            'weekly_base': 12000,
            'volatility': 0.5,
            'frequency': 0.5
        },
        'volatile': {
            'weekly_base': 18000,
            'volatility': 0.8,
            'frequency': 0.3
        },
        'seasonal': {
            'weekly_base': 14000,
            'volatility': 0.6,
            'frequency': 0.4,
            'seasonal_factor': True
        },
        'growing': {
            'weekly_base': 10000,
            'volatility': 0.4,
            'frequency': 0.6,
            'growth_rate': 0.02  # 2% monthly growth
        },
        'declining': {
            'weekly_base': 20000,
            'volatility': 0.5,
            'frequency': 0.5,
            'decline_rate': 0.015  # 1.5% monthly decline
        }
    }
    
    def __init__(self, pattern: str = 'moderate'):
        self.pattern = self.INCOME_PATTERNS.get(pattern, self.INCOME_PATTERNS['moderate'])
        self.pattern_name = pattern
        self.balance = 50000.0  # Starting balance
        self.month_counter = 0
        self.week_counter = 0
    
    def generate_income_transaction(self, date: datetime) -> Dict:
        """Generate a realistic income transaction"""
        # Decide if income occurs today
        if random.random() > self.pattern['frequency']:
            return None
        
        # Choose income category with weights
        category_weights = {
            MerchantCategory.FREELANCING: 0.5,
            MerchantCategory.PLATFORM_PAYOUT: 0.3,
            MerchantCategory.UPI_CREDIT: 0.2
        }
        category = random.choices(
            list(category_weights.keys()),
            weights=list(category_weights.values())
        )[0]
        
        # Generate amount based on pattern
        base_daily = self.pattern['weekly_base'] / 7
        volatility = self.pattern['volatility']
        
        # Apply growth/decline if applicable
        if 'growth_rate' in self.pattern:
            growth_factor = (1 + self.pattern['growth_rate']) ** self.month_counter
            base_daily *= growth_factor
        elif 'decline_rate' in self.pattern:
            decline_factor = (1 - self.pattern['decline_rate']) ** self.month_counter
            base_daily *= decline_factor
        
        # Apply seasonal factor if applicable
        if self.pattern.get('seasonal_factor'):
            # Higher income in Q4 (Oct-Dec), lower in Q2 (Apr-Jun)
            month = date.month
            if month in [10, 11, 12]:  # Q4
                base_daily *= 1.3
            elif month in [4, 5, 6]:  # Q2
                base_daily *= 0.7
        
        # Add randomness
        amount = base_daily * random.uniform(1 - volatility, 1 + volatility)
        
        # Platform payouts tend to be weekly/bi-weekly and larger
        if category == MerchantCategory.PLATFORM_PAYOUT:
            if random.random() < 0.3:  # 30% chance of payout
                amount = amount * random.uniform(5, 10)
            else:
                return None
        
        # Freelancing can have large project payments
        if category == MerchantCategory.FREELANCING:
            if random.random() < 0.2:  # 20% chance of large payment
                amount = amount * random.uniform(3, 8)
        
        amount = round(amount, 2)
        self.balance += amount
        
        description = random.choice(self.INCOME_DESCRIPTIONS[category])
        
        # Add realistic timestamp (business hours)
        hour = random.randint(9, 20)
        minute = random.randint(0, 59)
        timestamp = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return {
            'transaction_id': uuid.uuid4(),
            'txn_timestamp': timestamp,
            'amount_inr': Decimal(str(amount)),
            'txn_type': TransactionType.CREDIT,
            'balance_after_txn': Decimal(str(round(self.balance, 2))),
            'description': description,
            'merchant_category': category,
            'is_income': True
        }
    
    def generate_expense_transactions(self, date: datetime) -> List[Dict]:
        """Generate realistic daily expenses"""
        transactions = []
        
        # Rent (once a month, first week)
        if date.day <= 7 and random.random() < 0.15:
            amount = random.uniform(8000, 15000)
            self.balance -= amount
            transactions.append({
                'transaction_id': uuid.uuid4(),
                'txn_timestamp': date.replace(hour=10, minute=0),
                'amount_inr': Decimal(str(round(amount, 2))),
                'txn_type': TransactionType.DEBIT,
                'balance_after_txn': Decimal(str(round(self.balance, 2))),
                'description': random.choice(self.EXPENSE_DESCRIPTIONS[MerchantCategory.RENT]),
                'merchant_category': MerchantCategory.RENT,
                'is_income': False
            })
        
        # Daily expenses (food, travel, etc.)
        num_daily_expenses = random.randint(1, 5)
        
        for _ in range(num_daily_expenses):
            # Choose expense category
            category_weights = {
                MerchantCategory.FOOD_DELIVERY: 0.3,
                MerchantCategory.TRAVEL: 0.25,
                MerchantCategory.SHOPPING: 0.15,
                MerchantCategory.UTILITIES: 0.1,
                MerchantCategory.MOBILE_RECHARGE: 0.1,
                MerchantCategory.ENTERTAINMENT: 0.1
            }
            
            category = random.choices(
                list(category_weights.keys()),
                weights=list(category_weights.values())
            )[0]
            
            # Amount ranges by category
            amount_ranges = {
                MerchantCategory.FOOD_DELIVERY: (150, 600),
                MerchantCategory.TRAVEL: (50, 300),
                MerchantCategory.SHOPPING: (200, 2000),
                MerchantCategory.UTILITIES: (500, 2000),
                MerchantCategory.MOBILE_RECHARGE: (200, 800),
                MerchantCategory.ENTERTAINMENT: (100, 500)
            }
            
            min_amt, max_amt = amount_ranges[category]
            amount = random.uniform(min_amt, max_amt)
            
            # Utilities and recharge less frequent
            if category in [MerchantCategory.UTILITIES, MerchantCategory.MOBILE_RECHARGE]:
                if random.random() > 0.1:  # Only 10% chance
                    continue
            
            self.balance -= amount
            
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            timestamp = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
            
            transactions.append({
                'transaction_id': uuid.uuid4(),
                'txn_timestamp': timestamp,
                'amount_inr': Decimal(str(round(amount, 2))),
                'txn_type': TransactionType.DEBIT,
                'balance_after_txn': Decimal(str(round(self.balance, 2))),
                'description': random.choice(self.EXPENSE_DESCRIPTIONS[category]),
                'merchant_category': category,
                'is_income': False
            })
        
        return transactions
    
    def generate_transactions(self, user_id: str, account_id: str, months: int = 6) -> List[Dict]:
        """Generate complete transaction history"""
        transactions = []
        
        end_date = datetime.now(IST)
        start_date = end_date - timedelta(days=months * 30)
        
        current_date = start_date
        
        while current_date <= end_date:
            # Track month and week for patterns
            if current_date.day == 1:
                self.month_counter += 1
            if current_date.weekday() == 0:  # Monday
                self.week_counter += 1
            
            # Generate income
            income_txn = self.generate_income_transaction(current_date)
            if income_txn:
                income_txn['user_id'] = user_id
                income_txn['account_id'] = account_id
                transactions.append(income_txn)
            
            # Generate expenses
            expense_txns = self.generate_expense_transactions(current_date)
            for exp_txn in expense_txns:
                exp_txn['user_id'] = user_id
                exp_txn['account_id'] = account_id
                transactions.append(exp_txn)
            
            current_date += timedelta(days=1)
        
        # Sort by timestamp
        transactions.sort(key=lambda x: x['txn_timestamp'])
        
        return transactions


def generate_test_users(count: int = 3) -> List[Dict]:
    """Generate test user data"""
    patterns = ['stable', 'moderate', 'volatile']
    users = []
    
    for i in range(count):
        pattern = patterns[i % len(patterns)]
        user_data = {
            'user_id': str(uuid.uuid4()),
            'email': f'testuser{i+1}@example.com',
            'full_name': f'Test User {i+1}',
            'phone': f'98765432{i:02d}',
            'password': 'TestPass123',  # Shorter password to avoid bcrypt limit
            'pattern': pattern,
            'occupation': 'Freelancer' if pattern == 'volatile' else 'Developer',
            'monthly_fixed_expenses': 12000 if pattern == 'stable' else 15000
        }
        users.append(user_data)
    
    return users
