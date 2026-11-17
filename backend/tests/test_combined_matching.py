
from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item


def create_user(email):
    user = User(
        name="Test User",
        email=email,
        password="test-password",
        is_verified=True
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_item(user, item_type, title, image_url=None):
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


def test_combined_matching_success(client, monkeypatch):
    with client.application.app_context():
        lost_user = create_user("lost-combined@mail.jiit.ac.in")
        found_user = create_user("found-combined@mail.jiit.ac.in")

        lost_item = create_item(
            lost_user, "lost", "Black Wallet", "https://example.com/1.jpg"
        )
        create_item(
            found_user, "found", "Black Wallet", "https://example.com/2.jpg"
        )

        monkeypatch.setattr(
            "routes.combined_matching.calculate_match_score",
            lambda item1, item2: 80
        )
        monkeypatch.setattr(
            "routes.combined_matching.calculate_image_similarity",
            lambda url1, url2: 90
        )

        token = create_token(lost_user)

        response = client.get(
            f"/api/items/{lost_item.id}/matched-items",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["matches"][0]["match_type"] == "text_and_image"
        assert response.json["matches"][0]["match_score"] == 84.0


def test_combined_matching_text_only(client, monkeypatch):
    with client.application.app_context():
        lost_user = create_user("lost-text@mail.jiit.ac.in")
        found_user = create_user("found-text@mail.jiit.ac.in")

        lost_item = create_item(lost_user, "lost", "Black Wallet")
        create_item(found_user, "found", "Black Wallet")

        monkeypatch.setattr(
            "routes.combined_matching.calculate_match_score",
            lambda item1, item2: 80
        )

        token = create_token(lost_user)

        response = client.get(
            f"/api/items/{lost_item.id}/matched-items",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["matches"][0]["match_type"] == "text"
        assert response.json["matches"][0]["match_score"] == 80


def test_combined_matching_image_only(client, monkeypatch):
    with client.application.app_context():
        lost_user = create_user("lost-image-only@mail.jiit.ac.in")
        found_user = create_user("found-image-only@mail.jiit.ac.in")

        lost_item = create_item(
            lost_user, "lost", "Black Wallet", "https://example.com/1.jpg"
        )
        create_item(
            found_user, "found", "Blue Bag", "https://example.com/2.jpg"
        )

        monkeypatch.setattr(
            "routes.combined_matching.calculate_match_score",
            lambda item1, item2: 0
        )
        monkeypatch.setattr(
            "routes.combined_matching.calculate_image_similarity",
            lambda url1, url2: 85
        )

        token = create_token(lost_user)

        response = client.get(
            f"/api/items/{lost_item.id}/matched-items",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["matches"][0]["match_type"] == "image"


def test_combined_matching_no_results(client, monkeypatch):
    with client.application.app_context():
        lost_user = create_user("lost-none@mail.jiit.ac.in")
        found_user = create_user("found-none@mail.jiit.ac.in")

        lost_item = create_item(
            lost_user, "lost", "Black Wallet", "https://example.com/1.jpg"
        )
        create_item(
            found_user, "found", "Blue Bag", "https://example.com/2.jpg"
        )

        monkeypatch.setattr(
            "routes.combined_matching.calculate_match_score",
            lambda item1, item2: 0
        )
        monkeypatch.setattr(
            "routes.combined_matching.calculate_image_similarity",
            lambda url1, url2: 30
        )

        token = create_token(lost_user)

        response = client.get(
            f"/api/items/{lost_item.id}/matched-items",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 0


def test_combined_matching_item_not_found(client):
    with client.application.app_context():
        user = create_user("missing-combined@mail.jiit.ac.in")
        token = create_token(user)

        response = client.get(
            "/api/items/99999/matched-items",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_combined_matching_without_token(client):
    response = client.get("/api/items/1/matched-items")

    assert response.status_code == 401

