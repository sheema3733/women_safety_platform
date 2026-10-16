from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hash password securely using scrypt or pbkdf2."""
    if not password:
        raise ValueError("Password cannot be empty")
    return generate_password_hash(password, method="scrypt")

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against stored hash."""
    if not password or not password_hash:
        return False
    return check_password_hash(password_hash, password)
