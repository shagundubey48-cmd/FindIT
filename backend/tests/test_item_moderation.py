
from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item


def create_user(email, is_admin=False):
    user = User(
        name="Test User",
        email=email,
        password="test-password",
        is_verified=True,
        is_admin=is_admin
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_item(user, status="active"):
    item = Item(
        user_id=user.id,
        title="Black Wallet",
        description="Black leather wallet",
        category="Accessories",
        campus="JIIT Noida",
        location="Library",
        item_type="found",
        item_date=date.today(),
        status=status
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


def test_admin_resolves_item_report(client):
    with client.application.app_context():
        admin = create_user(
            "admin-resolve@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-resolve@mail.jiit.ac.in")
        item = create_item(reporter)
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/items/{item.id}/moderation",
            json={
                "status": "resolved",
                "admin_remarks": "The item has been returned to its owner."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["item"]["status"] == "resolved"
        assert response.json["item"]["admin_remarks"] == (
            "The item has been returned to its owner."
        )
        assert response.json["item"]["moderated_at"] is not None


def test_admin_removes_item_report(client):
    with client.application.app_context():
        admin = create_user(
            "admin-remove@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-remove@mail.jiit.ac.in")
        item = create_item(reporter)
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/items/{item.id}/moderation",
            json={
                "status": "removed",
                "admin_remarks": "Duplicate report."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["item"]["status"] == "removed"

        # The record is preserved rather than permanently deleted.
        assert db.session.get(Item, item.id) is not None


def test_admin_restores_item_report(client):
    with client.application.app_context():
        admin = create_user(
            "admin-restore@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-restore@mail.jiit.ac.in")
        item = create_item(reporter, status="removed")
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/items/{item.id}/moderation",
            json={
                "status": "active",
                "admin_remarks": "Report reviewed and restored."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["item"]["status"] == "active"


def test_admin_moderation_rejects_invalid_status(client):
    with client.application.app_context():
        admin = create_user(
            "admin-invalid-status@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-invalid-status@mail.jiit.ac.in")
        item = create_item(reporter)
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/items/{item.id}/moderation",
            json={
                "status": "deleted",
                "admin_remarks": "Invalid status test."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400

        db.session.refresh(item)
        assert item.status == "active"


def test_student_cannot_moderate_item(client):
    with client.application.app_context():
        student = create_user("student-moderate@mail.jiit.ac.in")
        reporter = create_user("reporter-moderate@mail.jiit.ac.in")
        item = create_item(reporter)
        token = create_token(student)

        response = client.patch(
            f"/api/admin/items/{item.id}/moderation",
            json={
                "status": "removed",
                "admin_remarks": "Attempted moderation."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403

        db.session.refresh(item)
        assert item.status == "active"


def test_admin_moderation_item_not_found(client):
    with client.application.app_context():
        admin = create_user(
            "admin-missing-item@mail.jiit.ac.in",
            is_admin=True
        )
        token = create_token(admin)

        response = client.patch(
            "/api/admin/items/99999/moderation",
            json={
                "status": "removed",
                "admin_remarks": "Test missing item."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_admin_cannot_moderate_claimed_item(client):
    with client.application.app_context():
        admin = create_user(
            "admin-claimed-item@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-claimed-item@mail.jiit.ac.in")
        item = create_item(reporter, status="claimed")
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/items/{item.id}/moderation",
            json={
                "status": "removed",
                "admin_remarks": "Attempted to remove claimed item."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 409

