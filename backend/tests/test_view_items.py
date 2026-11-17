
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


# Create a sample item report
def create_test_item(user, item_type="lost", title="Black Wallet"):
    item = Item(
        user_id=user.id,
        title=title,
        description="Sample item description",
        category="Accessories",
        campus="JIIT Sector 62",
        location="Library",
        item_type=item_type,
        item_date=datetime.strptime(
            "2026-11-15", "%Y-%m-%d"
        ).date(),
        status="active"
    )

    db.session.add(item)
    db.session.commit()

    return item


# Check retrieval of all active items
def test_get_all_items(client):
    user, token = create_authenticated_user()

    create_test_item(user, "lost", "Black Wallet")
    create_test_item(user, "found", "Blue Bottle")

    response = client.get(
        "/api/items",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 2
    assert len(response.json["items"]) == 2


# Check filtering of lost items
def test_get_lost_items(client):
    user, token = create_authenticated_user()

    create_test_item(user, "lost", "Black Wallet")
    create_test_item(user, "found", "Blue Bottle")

    response = client.get(
        "/api/items?type=lost",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["items"][0]["item_type"] == "lost"


# Check filtering of found items
def test_get_found_items(client):
    user, token = create_authenticated_user()

    create_test_item(user, "lost", "Black Wallet")
    create_test_item(user, "found", "Blue Bottle")

    response = client.get(
        "/api/items?type=found",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["items"][0]["item_type"] == "found"


# Check retrieval of individual item details
def test_get_item_details(client):
    user, token = create_authenticated_user()
    item = create_test_item(user)

    response = client.get(
        f"/api/items/{item.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["item"]["id"] == item.id
    assert response.json["item"]["title"] == "Black Wallet"


# Reject requests for nonexistent items
def test_get_nonexistent_item(client):
    user, token = create_authenticated_user()

    response = client.get(
        "/api/items/9999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


# Reject unsupported item type filters
def test_get_items_invalid_type(client):
    user, token = create_authenticated_user()

    response = client.get(
        "/api/items?type=other",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


# Reject item listing requests without authentication
def test_get_items_without_token(client):
    response = client.get("/api/items")

    assert response.status_code == 401

