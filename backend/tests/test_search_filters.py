
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


# Create a sample item
def create_test_item(user, title, description, category, campus, item_type):
    item = Item(
        user_id=user.id,
        title=title,
        description=description,
        category=category,
        campus=campus,
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


# Check keyword search in item title
def test_search_items_by_title(client):
    user, token = create_authenticated_user()

    create_test_item(
        user, "Black Wallet", "Leather wallet",
        "Accessories", "JIIT Sector 62", "lost"
    )

    create_test_item(
        user, "Blue Bottle", "Steel water bottle",
        "Accessories", "JIIT Sector 128", "found"
    )

    response = client.get(
        "/api/items?q=wallet",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["items"][0]["title"] == "Black Wallet"


# Check keyword search in item description
def test_search_items_by_description(client):
    user, token = create_authenticated_user()

    create_test_item(
        user, "Black Wallet", "Contains a student ID card",
        "Accessories", "JIIT Sector 62", "lost"
    )

    response = client.get(
        "/api/items?q=student ID",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 1


# Check category filtering
def test_filter_items_by_category(client):
    user, token = create_authenticated_user()

    create_test_item(
        user, "Black Wallet", "Leather wallet",
        "Accessories", "JIIT Sector 62", "lost"
    )

    create_test_item(
        user, "Notebook", "Blue notebook",
        "Stationery", "JIIT Sector 62", "found"
    )

    response = client.get(
        "/api/items?category=Accessories",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["items"][0]["category"] == "Accessories"


# Check campus filtering
def test_filter_items_by_campus(client):
    user, token = create_authenticated_user()

    create_test_item(
        user, "Black Wallet", "Leather wallet",
        "Accessories", "JIIT Sector 62", "lost"
    )

    create_test_item(
        user, "Blue Bottle", "Steel bottle",
        "Accessories", "JIIT Sector 128", "found"
    )

    response = client.get(
        "/api/items?campus=JIIT Sector 62",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["items"][0]["campus"] == "JIIT Sector 62"


# Check that multiple filters work together
def test_search_items_with_combined_filters(client):
    user, token = create_authenticated_user()

    create_test_item(
        user, "Black Wallet", "Leather wallet",
        "Accessories", "JIIT Sector 62", "lost"
    )

    create_test_item(
        user, "Black Backpack", "Large backpack",
        "Bags", "JIIT Sector 62", "found"
    )

    create_test_item(
        user, "Black Wallet", "Leather wallet",
        "Accessories", "JIIT Sector 128", "found"
    )

    response = client.get(
        "/api/items?q=black&type=lost&category=Accessories&campus=JIIT Sector 62",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["items"][0]["title"] == "Black Wallet"
    assert response.json["items"][0]["item_type"] == "lost"


# Return an empty list when no matching item exists
def test_search_items_no_results(client):
    user, token = create_authenticated_user()

    response = client.get(
        "/api/items?q=nonexistent",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 0
    assert response.json["items"] == []


# Reject search requests without authentication
def test_search_items_without_token(client):
    response = client.get("/api/items?q=wallet")

    assert response.status_code == 401

