
from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item
from models.claim import Claim


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


def create_claim(claimant, status="pending"):
    reporter = create_user(
        f"reporter-{claimant.id}@mail.jiit.ac.in"
    )

    item = Item(
        user_id=reporter.id,
        title="Black Wallet",
        description="Black leather wallet",
        category="Accessories",
        campus="JIIT Noida",
        location="Library",
        item_type="found",
        item_date=date.today(),
        status="active"
    )

    db.session.add(item)
    db.session.commit()

    claim = Claim(
        claimant_id=claimant.id,
        item_id=item.id,
        ownership_details="This wallet belongs to me.",
        status=status,
        admin_remarks=None
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


def test_track_pending_claim_status(client):
    with client.application.app_context():
        user = create_user("status-pending@mail.jiit.ac.in")
        claim = create_claim(user)
        token = create_token(user)

        response = client.get(
            f"/api/claims/{claim.id}/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["status"] == "pending"
        assert response.json["admin_remarks"] is None
        assert response.json["status_updated_at"]


def test_track_approved_claim_status(client):
    with client.application.app_context():
        user = create_user("status-approved@mail.jiit.ac.in")
        claim = create_claim(user, status="approved")
        claim.admin_remarks = "Ownership verified."
        db.session.commit()

        token = create_token(user)

        response = client.get(
            f"/api/claims/{claim.id}/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["status"] == "approved"
        assert response.json["admin_remarks"] == "Ownership verified."


def test_track_rejected_claim_status(client):
    with client.application.app_context():
        user = create_user("status-rejected@mail.jiit.ac.in")
        claim = create_claim(user, status="rejected")
        claim.admin_remarks = "The submitted proof was insufficient."
        db.session.commit()

        token = create_token(user)

        response = client.get(
            f"/api/claims/{claim.id}/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["status"] == "rejected"
        assert response.json["admin_remarks"] == (
            "The submitted proof was insufficient."
        )


def test_user_cannot_track_another_users_claim(client):
    with client.application.app_context():
        claimant = create_user("claim-owner@mail.jiit.ac.in")
        another_user = create_user("claim-outsider@mail.jiit.ac.in")

        claim = create_claim(claimant)
        token = create_token(another_user)

        response = client.get(
            f"/api/claims/{claim.id}/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_track_nonexistent_claim(client):
    with client.application.app_context():
        user = create_user("status-missing@mail.jiit.ac.in")
        token = create_token(user)

        response = client.get(
            "/api/claims/99999/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_claim_status_requires_authentication(client):
    response = client.get("/api/claims/1/status")

    assert response.status_code == 401

