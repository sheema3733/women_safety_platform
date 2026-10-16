import pytest
from app.database import db_session
from app.models.user import User

def test_user_registration_success(client):
    response = client.post("/register", data={
        "full_name": "Alice Wonder",
        "email": "alice@example.com",
        "password": "Password@123",
        "confirm_password": "Password@123",
        "phone": "+1 555-0155",
        "city": "Metropolis"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Alice Wonder" in response.data or b"Registration successful" in response.data

    user = db_session.query(User).filter_by(email="alice@example.com").first()
    assert user is not None
    assert user.full_name == "Alice Wonder"
    assert user.role.name == "USER"

def test_user_registration_password_validation(client):
    # Weak password (no uppercase or numbers)
    response = client.post("/register", data={
        "full_name": "Bob Smith",
        "email": "bob@example.com",
        "password": "short",
        "confirm_password": "short"
    })
    assert response.status_code == 200
    assert b"Password must be at least 8 characters long" in response.data

def test_user_registration_duplicate_email(client, test_user):
    response = client.post("/register", data={
        "full_name": "Duplicate User",
        "email": test_user.email,
        "password": "Password@123",
        "confirm_password": "Password@123"
    })
    assert response.status_code == 200
    assert b"An account with this email already exists" in response.data

def test_user_login_success(client, test_user):
    response = client.post("/login", data={
        "email": test_user.email,
        "password": "UserPass@123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Personal Safety Readiness Score" in response.data

def test_user_login_invalid_password(client, test_user):
    response = client.post("/login", data={
        "email": test_user.email,
        "password": "WrongPassword999"
    })
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_user_logout(auth_user_client):
    response = auth_user_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been safely logged out" in response.data
