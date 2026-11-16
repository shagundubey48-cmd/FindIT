
import pytest
from app import create_app, db
from config import TestConfig
from models.user import User

@pytest.fixture
def app():
    # Create Flask app with testing configuration
    app = create_app(TestConfig)

    with app.app_context():
        # Create database tables before tests
        db.create_all()

        yield app

        # Remove test tables after tests
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    # Provide a test client for API requests
    return app.test_client()

