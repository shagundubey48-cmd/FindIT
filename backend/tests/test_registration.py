
import hashlib
from datetime import datetime, timedelta, timezone

from app import db
from models.user import User


# Check registration when name is missing
def test_registration_requires_name(client):
    response = client.post("/api/register", json={
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })
    assert response.status_code == 400


# Check registration when email is missing
def test_registration_requires_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "password": "Test@123"
    })
    assert response.status_code == 400


# Check registration when password is missing
def test_registration_requires_password(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in"
    })
    assert response.status_code == 400


# Check successful registration
def test_registration_success(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })
    assert response.status_code == 201
    assert response.json["message"] == (
        "Registration successful. Please verify your email."
    )


# Reject invalid email format
def test_registration_rejects_invalid_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "invalid-email",
        "password": "Test@123"
    })
    assert response.status_code == 400


# Reject duplicate email registration
def test_registration_rejects_duplicate_email(client):
    data = {
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    }

    client.post("/api/register", json=data)
    response = client.post("/api/register", json=data)

    assert response.status_code == 409


# Reject weak passwords
def test_registration_rejects_weak_password(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "weak"
    })
    assert response.status_code == 400


# Reject non-college email addresses
def test_registration_rejects_non_college_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@gmail.com",
        "password": "Test@123"
    })
    assert response.status_code == 400


# Accept valid college email addresses
def test_registration_accepts_college_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })
    assert response.status_code == 201


# Check that registration creates an unverified account
def test_registration_creates_unverified_account(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 201

    user = User.query.filter_by(
        email="student@mail.jiit.ac.in"
    ).first()

    assert user is not None
    assert user.is_verified is False
    assert user.verification_token_hash is not None
    assert user.verification_token_expires_at is not None


# Check successful email verification
def test_email_verification_success(client):
    token = "valid-test-token"

    user = User(
        name="Test Student",
        email="verify@mail.jiit.ac.in",
        password="hashed-password",
        is_verified=False,
        verification_token_hash=hashlib.sha256(
            token.encode()
        ).hexdigest(),
        verification_token_expires_at=(
            datetime.now(timezone.utc).replace(tzinfo=None)
            + timedelta(minutes=15)
        )
    )

    db.session.add(user)
    db.session.commit()

    response = client.get(f"/api/verify/{token}")

    assert response.status_code == 200

    db.session.refresh(user)

    assert user.is_verified is True
    assert user.verification_token_hash is None
    assert user.verification_token_expires_at is None


# Reject invalid verification tokens
def test_email_verification_rejects_invalid_token(client):
    response = client.get("/api/verify/invalid-token")
    assert response.status_code == 400


# Reject expired verification tokens
def test_email_verification_rejects_expired_token(client):
    token = "expired-test-token"

    user = User(
        name="Test Student",
        email="expired@mail.jiit.ac.in",
        password="hashed-password",
        is_verified=False,
        verification_token_hash=hashlib.sha256(
            token.encode()
        ).hexdigest(),
        verification_token_expires_at=(
            datetime.now(timezone.utc).replace(tzinfo=None)
            - timedelta(minutes=1)
        )
    )

    db.session.add(user)
    db.session.commit()

    response = client.get(f"/api/verify/{token}")

    assert response.status_code == 400

    db.session.refresh(user)
    assert user.is_verified is False
