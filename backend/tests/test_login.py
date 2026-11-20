
from werkzeug.security import generate_password_hash
from models.user import User
from app import db
import jwt


# Create a test user for login tests
def create_test_user(verified=True):
    user = User(
        name="Test Student",
        email="student@mail.jiit.ac.in",
        password=generate_password_hash("Test@123"),
        is_verified=verified
    )
    db.session.add(user)
    db.session.commit()
    return user


# Reject login when email or password is missing
def test_login_requires_email_and_password(client):
    response = client.post("/api/login", json={
        "email": "student@mail.jiit.ac.in"
    })
    assert response.status_code == 400


# Reject login for an unknown email
def test_login_rejects_unknown_email(client):
    response = client.post("/api/login", json={
        "email": "unknown@mail.jiit.ac.in",
        "password": "Test@123"
    })
    assert response.status_code == 401


# Reject login when password is incorrect
def test_login_rejects_wrong_password(client):
    create_test_user()

    response = client.post("/api/login", json={
        "email": "student@mail.jiit.ac.in",
        "password": "Wrong@123"
    })
    assert response.status_code == 401


# Allow verified users to log in
def test_login_success(client):
    user = create_test_user(verified=True)

    response = client.post("/api/login", json={
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 200
    assert response.json["message"] == "Login successful"
    assert response.json["user"]["id"] == user.id
    assert "token" in response.json


# Check that the returned JWT contains the correct user ID
def test_login_returns_valid_jwt(client):
    user = create_test_user(verified=True)

    response = client.post("/api/login", json={
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })

    token = response.json["token"]

    decoded = jwt.decode(
        token,
        "test-secret",
        algorithms=["HS256"]
    )

    assert decoded["sub"] == str(user.id)

