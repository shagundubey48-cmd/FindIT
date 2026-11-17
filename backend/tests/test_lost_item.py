
from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import generate_password_hash

from app import db
from models.user import User
from models.item import Item


# Create a verified user and authentication token
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


# Sample lost-item report
def get_lost_item_data():
    return {
        "title": "Black Wallet",
        "description": "Black leather wallet with student ID",
        "category": "Accessories",
        "campus": "JIIT Sector 62",
        "location": "Library",
        "item_date": "2026-11-15"
    }


# Check successful lost-item reporting
def test_report_lost_item_success(client):
    user, token = create_authenticated_user()

    response = client.post(
        "/api/items/lost",
        json=get_lost_item_data(),
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert response.json["message"] == "Lost item reported successfully"

    item = Item.query.first()

    assert item is not None
    assert item.user_id == user.id
    assert item.item_type == "lost"


# Reject lost-item reporting without authentication
def test_report_lost_item_without_token(client):
    response = client.post(
        "/api/items/lost",
        json=get_lost_item_data()
    )

    assert response.status_code == 401


# Reject requests with missing fields
def test_report_lost_item_missing_fields(client):
    user, token = create_authenticated_user()

    response = client.post(
        "/api/items/lost",
        json={"title": "Black Wallet"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


# Reject invalid date formats
def test_report_lost_item_invalid_date(client):
    user, token = create_authenticated_user()

    data = get_lost_item_data()
    data["item_date"] = "15-11-2026"

    response = client.post(
        "/api/items/lost",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


# Reject empty text fields
def test_report_lost_item_empty_title(client):
    user, token = create_authenticated_user()

    data = get_lost_item_data()
    data["title"] = "   "

    response = client.post(
        "/api/items/lost",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


# Check that the report is associated with its creator
def test_lost_item_belongs_to_logged_in_user(client):
    user, token = create_authenticated_user()

    client.post(
        "/api/items/lost",
        json=get_lost_item_data(),
        headers={"Authorization": f"Bearer {token}"}
    )

    item = Item.query.first()

    assert item.user_id == user.id

