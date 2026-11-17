
from werkzeug.security import generate_password_hash
from models.user import User
from app import db
import jwt
from datetime import datetime, timedelta, timezone


# Create a verified test user and generate an authentication token
def create_authenticated_user():
    user = User(
        name="Test Student",
        email="student@mail.jiit.ac.in",
        password=generate_password_hash("Test@123"),
        is_verified=True
    )

    db.session.add(user)
    db.session.commit()

    token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        },
        "test-secret",
        algorithm="HS256"
    )

    return user, token


# Check successful profile retrieval
def test_get_profile_success(client):
    user, token = create_authenticated_user()

    response = client.get(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["name"] == user.name
    assert response.json["email"] == user.email


# Reject profile access without a token
def test_get_profile_without_token(client):
    response = client.get("/api/profile")
    assert response.status_code == 401


# Reject profile access with an invalid token
def test_get_profile_with_invalid_token(client):
    response = client.get(
        "/api/profile",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401


# Check successful profile update
def test_update_profile_success(client):
    user, token = create_authenticated_user()

    response = client.put(
        "/api/profile",
        json={"name": "Updated Student"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["user"]["name"] == "Updated Student"


# Reject profile update without a token
def test_update_profile_without_token(client):
    response = client.put(
        "/api/profile",
        json={"name": "Updated Student"}
    )

    assert response.status_code == 401


# Reject an empty profile name
def test_update_profile_with_empty_name(client):
    user, token = create_authenticated_user()

    response = client.put(
        "/api/profile",
        json={"name": "   "},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400

