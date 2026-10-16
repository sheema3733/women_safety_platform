import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-production-safe-key-women-safety-platform-2026")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    APP_NAME = "Women Safety & Emergency Assistance Platform"
    APP_TAGLINE = "Preparedness, Community Care & Rapid Assistance"
    DISCLAIMER_TEXT = (
        "This platform is a safety-assistance application and does not replace official "
        "police, ambulance, government emergency services, or professional emergency response systems."
    )
    READINESS_DISCLAIMER = (
        "Safety Readiness reflects preparedness activities completed on the platform. "
        "It does not guarantee personal safety."
    )

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'women_safety_dev.db')}"
    )

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'women_safety.db')}"
    )

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
