
from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import generate_password_hash

from app import db
from models.user import User
from models.item import Item


# Create a verified user and authentication token
def create_user(email):
    user = User(
        name="Test Student",
        email=email,
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


# Create a sample lost or found item
def create_item(user, item_type, title, description):
    item = Item(
        user_id=user.id,
        title=title,
        description=description,
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


# Check successful text-based matching
def test_text_matching_success(client):
    lost_user, token = create_user("lost@mail.jiit.ac.in")
    found_user, _ = create_user("found@mail.jiit.ac.in")

    lost_item = create_item(
        lost_user,
        "lost",
        "Black Leather Wallet",
        "Black wallet containing student identity card"
    )

    create_item(
        found_user,
        "found",
        "Black Leather Wallet",
        "Found a black wallet with an identity card"
    )

    response = client.get(
        f"/api/items/{lost_item.id}/matches",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["matches"][0]["score"] > 20


# Ensure only opposite item types are matched
def test_text_matching_opposite_type_only(client):
    lost_user, token = create_user("lost@mail.jiit.ac.in")
    found_user, _ = create_user("found@mail.jiit.ac.in")

    lost_item = create_item(
        lost_user, "lost", "Black Wallet", "Black leather wallet"
    )

    create_item(
        found_user, "lost", "Black Wallet", "Black leather wallet"
    )

    response = client.get(
        f"/api/items/{lost_item.id}/matches",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 0


# Do not match reports created by the same user
def test_text_matching_excludes_same_user(client):
    user, token = create_user("student@mail.jiit.ac.in")

    lost_item = create_item(
        user, "lost", "Black Wallet", "Black leather wallet"
    )

    create_item(
        user, "found", "Black Wallet", "Black leather wallet"
    )

    response = client.get(
        f"/api/items/{lost_item.id}/matches",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 0


# Return no matches when no similar item exists
def test_text_matching_no_results(client):
    lost_user, token = create_user("lost@mail.jiit.ac.in")
    found_user, _ = create_user("found@mail.jiit.ac.in")

    lost_item = create_item(
        lost_user, "lost", "Black Wallet", "Leather wallet"
    )

    create_item(
        found_user, "found", "Blue Notebook", "Paper notebook"
    )

    response = client.get(
        f"/api/items/{lost_item.id}/matches",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["count"] == 0


# Reject matching requests without authentication
def test_text_matching_without_token(client):
    response = client.get("/api/items/1/matches")

    assert response.status_code == 401

