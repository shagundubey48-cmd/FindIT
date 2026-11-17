
def test_registration_requires_name(client):
    response = client.post("/api/register", json={
        "email": "student@jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 400


def test_registration_requires_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "password": "Test@123"
    })

    assert response.status_code == 400


def test_registration_requires_password(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in"
    })

    assert response.status_code == 400


def test_registration_success(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 201
    assert response.json["message"] == "Registration successful"

def test_registration_rejects_invalid_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "invalid-email",
        "password": "Test@123"
    })

    assert response.status_code == 400


def test_registration_rejects_duplicate_email(client):
    data = {
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    }

    client.post("/api/register", json=data)
    response = client.post("/api/register", json=data)

    assert response.status_code == 409


def test_registration_rejects_weak_password(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student2@mail.jiit.ac.in",
        "password": "123"
    })

    assert response.status_code == 400


def test_registration_rejects_non_college_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@gmail.com",
        "password": "Test@123"
    })

    assert response.status_code == 400


def test_registration_accepts_college_email(client):
    response = client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })

    assert response.status_code == 201
    assert response.json["message"] == "Registration successful"


import hashlib
from datetime import datetime, timedelta, timezone
from models.user import User
from app import db


def test_registration_creates_unverified_account(client):
    client.post("/api/register", json={
        "name": "Test Student",
        "email": "student@mail.jiit.ac.in",
        "password": "Test@123"
    })

    user = User.query.filter_by(
        email="student@mail.jiit.ac.in"
    ).first()

    assert user is not None
    assert user.is_verified is False
    assert user.verification_token_hash is not None
    assert user.verification_token_expires_at is not None


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
        verification_token_expires_at=datetime.now(timezone.utc)
        .replace(tzinfo=None) + timedelta(minutes=15)
    )

    db.session.add(user)
    db.session.commit()

    response = client.get(f"/api/verify/{token}")

    assert response.status_code == 200

    db.session.refresh(user)
    assert user.is_verified is True
    assert user.verification_token_hash is None


def test_email_verification_rejects_invalid_token(client):
    response = client.get("/api/verify/invalid-token")

    assert response.status_code == 400


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
        verification_token_expires_at=datetime.now(timezone.utc)
        .replace(tzinfo=None) - timedelta(minutes=1)
    )

    db.session.add(user)
    db.session.commit()

    response = client.get(f"/api/verify/{token}")

    assert response.status_code == 400

    db.session.refresh(user)
    assert user.is_verified is False

