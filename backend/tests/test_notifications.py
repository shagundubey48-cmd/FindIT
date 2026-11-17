
from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item
from models.notification import Notification
from services.notification_service import create_match_notifications


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


def create_item(user, item_type, title):
    item = Item(
        user_id=user.id,
        title=title,
        description="Test item description",
        category="Accessories",
        campus="JIIT Noida",
        location="Campus",
        item_type=item_type,
        item_date=date.today(),
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


def test_match_creates_notifications_for_both_users(client):
    with client.application.app_context():
        lost_user = create_user("lost-notify@mail.jiit.ac.in")
        found_user = create_user("found-notify@mail.jiit.ac.in")

        lost_item = create_item(lost_user, "lost", "Black Wallet")
        found_item = create_item(found_user, "found", "Black Wallet")

        create_match_notifications(lost_item, found_item)

        notifications = Notification.query.all()

        assert len(notifications) == 2
        assert {n.user_id for n in notifications} == {
            lost_user.id, found_user.id
        }


def test_duplicate_match_does_not_create_duplicate_notifications(client):
    with client.application.app_context():
        lost_user = create_user("lost-duplicate@mail.jiit.ac.in")
        found_user = create_user("found-duplicate@mail.jiit.ac.in")

        lost_item = create_item(lost_user, "lost", "Black Wallet")
        found_item = create_item(found_user, "found", "Black Wallet")

        create_match_notifications(lost_item, found_item)
        create_match_notifications(lost_item, found_item)

        assert Notification.query.count() == 2


def test_get_notifications_success(client):
    with client.application.app_context():
        lost_user = create_user("lost-get@mail.jiit.ac.in")
        found_user = create_user("found-get@mail.jiit.ac.in")

        lost_item = create_item(lost_user, "lost", "Black Wallet")
        found_item = create_item(found_user, "found", "Black Wallet")

        create_match_notifications(lost_item, found_item)

        token = create_token(lost_user)

        response = client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["unread_count"] == 1


def test_users_only_see_their_own_notifications(client):
    with client.application.app_context():
        lost_user = create_user("lost-private@mail.jiit.ac.in")
        found_user = create_user("found-private@mail.jiit.ac.in")

        lost_item = create_item(lost_user, "lost", "Black Wallet")
        found_item = create_item(found_user, "found", "Black Wallet")

        create_match_notifications(lost_item, found_item)

        token = create_token(lost_user)

        response = client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.json["count"] == 1
        assert response.json["notifications"][0]["message"]


def test_mark_notification_as_read(client):
    with client.application.app_context():
        lost_user = create_user("lost-read@mail.jiit.ac.in")
        found_user = create_user("found-read@mail.jiit.ac.in")

        lost_item = create_item(lost_user, "lost", "Black Wallet")
        found_item = create_item(found_user, "found", "Black Wallet")

        create_match_notifications(lost_item, found_item)

        notification = Notification.query.filter_by(
            user_id=lost_user.id
        ).first()

        token = create_token(lost_user)

        response = client.patch(
            f"/api/notifications/{notification.id}/read",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["notification"]["is_read"] is True


def test_user_cannot_mark_another_users_notification_as_read(client):
    with client.application.app_context():
        lost_user = create_user("lost-owner@mail.jiit.ac.in")
        found_user = create_user("found-owner@mail.jiit.ac.in")

        lost_item = create_item(lost_user, "lost", "Black Wallet")
        found_item = create_item(found_user, "found", "Black Wallet")

        create_match_notifications(lost_item, found_item)

        notification = Notification.query.filter_by(
            user_id=found_user.id
        ).first()

        token = create_token(lost_user)

        response = client.patch(
            f"/api/notifications/{notification.id}/read",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_mark_nonexistent_notification_as_read(client):
    with client.application.app_context():
        user = create_user("missing-notification@mail.jiit.ac.in")
        token = create_token(user)

        response = client.patch(
            "/api/notifications/99999/read",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_notifications_require_authentication(client):
    response = client.get("/api/notifications")

    assert response.status_code == 401

