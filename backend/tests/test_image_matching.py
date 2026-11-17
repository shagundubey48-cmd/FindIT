
from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item


def create_test_user(email):
    user = User(
        name="Test User",
        email=email,
        password="test-password",
        is_verified=True
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_test_item(user, item_type, title, image_url):
    item = Item(
        user_id=user.id,
        title=title,
        description="Test item description",
        category="Accessories",
        campus="JIIT Noida",
        location="Campus",
        item_type=item_type,
        item_date=date.today(),
        image_url=image_url,
        status="active"
    )
    db.session.add(item)
    db.session.commit()
    return item


def create_token(user):
    return jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        TestConfig.SECRET_KEY,
        algorithm="HS256"
    )


def test_image_matching_success(client, monkeypatch):
    with client.application.app_context():
        lost_user = create_test_user("lost-image@mail.jiit.ac.in")
        found_user = create_test_user("found-image@mail.jiit.ac.in")

        lost_item = create_test_item(
            lost_user, "lost", "Black Wallet", "https://example.com/lost.jpg"
        )
        create_test_item(
            found_user, "found", "Wallet Found",
            "https://example.com/found.jpg"
        )

        monkeypatch.setattr(
            "routes.image_matching.calculate_image_similarity",
            lambda url1, url2: 92.5
        )

        token = create_token(lost_user)

        response = client.get(
            f"/api/items/{lost_item.id}/image-matches",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["matches"][0]["similarity_score"] == 92.5


def test_image_matching_excludes_low_similarity(client, monkeypatch):
    with client.application.app_context():
        lost_user = create_test_user("lost-low@mail.jiit.ac.in")
        found_user = create_test_user("found-low@mail.jiit.ac.in")

        lost_item = create_test_item(
            lost_user, "lost", "Black Wallet", "https://example.com/1.jpg"
        )
        create_test_item(
            found_user, "found", "Blue Bag", "https://example.com/2.jpg"
        )

        monkeypatch.setattr(
            "routes.image_matching.calculate_image_similarity",
            lambda url1, url2: 40.0
        )

        token = create_token(lost_user)

        response = client.get(
            f"/api/items/{lost_item.id}/image-matches",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 0


def test_image_matching_without_item_image(client):
    with client.application.app_context():
        user = create_test_user("no-image@mail.jiit.ac.in")

        item = create_test_item(
            user, "lost", "Black Wallet", None
        )

        token = create_token(user)

        response = client.get(
            f"/api/items/{item.id}/image-matches",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 0


def test_image_matching_item_not_found(client):
    with client.application.app_context():
        user = create_test_user("missing-item@mail.jiit.ac.in")
        token = create_token(user)

        response = client.get(
            "/api/items/99999/image-matches",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_image_matching_without_token(client):
    response = client.get("/api/items/1/image-matches")

    assert response.status_code == 401

