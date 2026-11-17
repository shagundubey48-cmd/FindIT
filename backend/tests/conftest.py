
import sys
from pathlib import Path

# Add the backend directory to Python's import path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import pytest
from app import create_app, db
from config import TestConfig


# Create a fresh test database for each test
@pytest.fixture
def app():
    app = create_app(TestConfig)
    app.config["ALLOWED_EMAIL_DOMAINS"] = ["mail.jiit.ac.in"]

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


# Provide Flask test client
@pytest.fixture
def client(app):
    return app.test_client()


# Prevent real verification emails during tests
@pytest.fixture(autouse=True)
def suppress_verification_emails(monkeypatch):
    monkeypatch.setattr(
        "routes.auth.send_verification_email",
        lambda email, token: None
    )
