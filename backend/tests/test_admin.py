
from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item
from models.claim import Claim


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


def create_item(user, item_type="found"):
    item = Item(
        user_id=user.id,
        title="Black Wallet",
        description="Black leather wallet",
        category="Accessories",
        campus="JIIT Noida",
        location="Library",
        item_type=item_type,
        item_date=date.today(),
        status="active"
    )
    db.session.add(item)
    db.session.commit()
    return item


def create_claim(claimant, item):
    claim = Claim(
        claimant_id=claimant.id,
        item_id=item.id,
        ownership_details="This wallet belongs to me.",
        status="pending"
    )
    db.session.add(claim)
    db.session.commit()
    return claim


def create_token(user):
    return jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        TestConfig.SECRET_KEY,
        algorithm="HS256"
    )


def test_admin_dashboard_success(client):
    with client.application.app_context():
        admin = create_user(
            "admin-dashboard@mail.jiit.ac.in",
            is_admin=True
        )
        student = create_user("student-dashboard@mail.jiit.ac.in")

        create_item(student, "lost")
        create_item(student, "found")

        token = create_token(admin)

        response = client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["total_users"] == 2
        assert response.json["total_items"] == 2
        assert response.json["active_lost_items"] == 1
        assert response.json["active_found_items"] == 1


def test_student_cannot_access_admin_dashboard(client):
    with client.application.app_context():
        student = create_user("ordinary-student@mail.jiit.ac.in")
        token = create_token(student)

        response = client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


def test_admin_can_view_all_items(client):
    with client.application.app_context():
        admin = create_user(
            "admin-items@mail.jiit.ac.in",
            is_admin=True
        )
        student = create_user("student-items@mail.jiit.ac.in")

        create_item(student, "lost")
        create_item(student, "found")

        token = create_token(admin)

        response = client.get(
            "/api/admin/items",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 2


def test_student_cannot_view_admin_items(client):
    with client.application.app_context():
        student = create_user("student-private-items@mail.jiit.ac.in")
        token = create_token(student)

        response = client.get(
            "/api/admin/items",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


def test_admin_can_view_all_claims(client):
    with client.application.app_context():
        admin = create_user(
            "admin-claims@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-claims@mail.jiit.ac.in")
        claimant = create_user("claimant-claims@mail.jiit.ac.in")

        item = create_item(reporter)
        create_claim(claimant, item)

        token = create_token(admin)

        response = client.get(
            "/api/admin/claims",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["claims"][0]["status"] == "pending"


def test_student_cannot_view_admin_claims(client):
    with client.application.app_context():
        student = create_user("student-private-claims@mail.jiit.ac.in")
        token = create_token(student)

        response = client.get(
            "/api/admin/claims",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


def test_admin_dashboard_requires_authentication(client):
    response = client.get("/api/admin/dashboard")

    assert response.status_code == 401

