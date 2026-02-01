import pytest
from fastapi import status
import uuid


def test_register_user(client):
    """Test user registration"""
    # Use unique email to avoid conflicts
    unique_email = f"newuser_{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "SecurePass123!",
            "full_name": "New User",
            "phone": "9876543211"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == unique_email
    assert data["full_name"] == "New User"
    assert "user_id" in data


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Duplicate User"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "TestPass123!"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "WrongPassword"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with nonexistent user"""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "Password123"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/auth/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


def test_get_current_user_no_auth(client):
    """Test getting current user without authentication"""
    response = client.get("/auth/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
