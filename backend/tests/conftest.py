
import sys
from pathlib import Path

# Add backend directory to Python import path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import pytest
from app import create_app, db
from config import TestConfig
from models.user import User


@pytest.fixture
def app():
    # Create Flask application using MySQL test configuration
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    # Create test client for API requests
    return app.test_client()
