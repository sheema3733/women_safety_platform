import pytest
from app.security.hashing import hash_password, verify_password
from app.validators.forms import validate_registration, ValidationError

def test_password_hashing_and_verification():
    raw_pass = "SecureSecret@2026"
    pwd_hash = hash_password(raw_pass)

    assert pwd_hash != raw_pass
    assert verify_password(raw_pass, pwd_hash) is True
    assert verify_password("WrongPassword", pwd_hash) is False

def test_registration_validation_checks():
    # Empty email
    with pytest.raises(ValidationError) as exc:
        validate_registration({"email": "", "full_name": "Test", "password": "Password1@"})
    assert "email" in exc.value.errors

    # Passwords do not match
    with pytest.raises(ValidationError) as exc:
        validate_registration({
            "email": "valid@email.com",
            "full_name": "Test User",
            "password": "Password1@",
            "confirm_password": "Password2@"
        })
    assert "confirm_password" in exc.value.errors

def test_custom_404_error_page(client):
    response = client.get("/non-existent-page-route-12345")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data

def test_custom_405_error_page(client):
    response = client.post("/about")
    assert response.status_code == 405
    assert b"Method Not Allowed" in response.data
