import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from app.database import Base
from app.models import (
    User, UserProfile, BankAccount, Transaction, IncomeSource,
    AIFeature, CashflowPrediction, SmoothingBuffer, WeeklyRelease,
    AIInsight, ModelVersion, ModelMetric, AuditLog
)
from app.config import get_settings

settings = get_settings()


def create_database():
    """Create database if it doesn't exist"""
    # Parse database URL
    db_url = settings.database_url
    parts = db_url.split('/')
    db_name = parts[-1]
    base_url = '/'.join(parts[:-1])
    
    # Connect to postgres database to create our database
    postgres_url = f"{base_url}/postgres"
    
    try:
        engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            )
            exists = result.fetchone()
            
            if not exists:
                conn.execute(text(f'CREATE DATABASE {db_name}'))
                print(f"✓ Database '{db_name}' created successfully")
            else:
                print(f"✓ Database '{db_name}' already exists")
        
        engine.dispose()
    except Exception as e:
        print(f"Error creating database: {e}")
        print(f"Attempting to continue with existing database...")
        # Database might already exist, continue


def init_tables():
    """Create all tables"""
    try:
        # Create engine for our database
        engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully")
        engine.dispose()
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise


if __name__ == "__main__":
    print("Initializing database...")
    create_database()
    init_tables()
    print("\n✓ Database initialization complete!")
