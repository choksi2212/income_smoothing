import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, UserProfile, BankAccount
from app.auth import get_password_hash
from decimal import Decimal
import hashlib

# Use production database for testing
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:niklaus2212@localhost:5432/income_smoothing"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Use production database for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Use existing test user from database or create one with bank account"""
    user = db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        # Create if doesn't exist
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("TestPass123!"),
            full_name="Test User",
            phone="9876543210"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create bank account for test user
        encrypted_number = hashlib.sha256("1234567890".encode()).hexdigest()
        account = BankAccount(
            user_id=user.user_id,
            account_number_encrypted=encrypted_number,
            bank_name="Test Bank",
            account_type="savings",
            is_primary=True,
            current_balance_inr=Decimal('50000.00')
        )
        db.add(account)
        db.commit()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers"""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "TestPass123!"}
    )
    if response.status_code != 200:
        # If login fails, print the error for debugging
        print(f"Login failed: {response.status_code} - {response.text}")
        # Return empty headers to avoid KeyError
        return {}
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
