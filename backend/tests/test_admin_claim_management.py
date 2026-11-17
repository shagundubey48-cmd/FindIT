
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


def create_item(user):
    item = Item(
        user_id=user.id,
        title="Black Wallet",
        description="Black leather wallet",
        category="Accessories",
        campus="JIIT Noida",
        location="Library",
        item_type="found",
        item_date=date.today(),
        image_url="https://example.com/wallet.jpg",
        status="active"
    )
    db.session.add(item)
    db.session.commit()
    return item


def create_claim(claimant, item):
    claim = Claim(
        claimant_id=claimant.id,
        item_id=item.id,
        ownership_details="My college ID is inside the wallet.",
        proof_type="identifying_mark",
        proof_details="My initials are engraved inside.",
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


def test_admin_view_claim_details(client):
    with client.application.app_context():
        admin = create_user(
            "admin-detail@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-detail@mail.jiit.ac.in")
        claimant = create_user("claimant-detail@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(admin)

        response = client.get(
            f"/api/admin/claims/{claim.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["claim"]["proof_type"] == "identifying_mark"
        assert response.json["claim"]["claimant_email"] == claimant.email


def test_student_cannot_view_admin_claim_details(client):
    with client.application.app_context():
        student = create_user("student-detail@mail.jiit.ac.in")
        token = create_token(student)

        response = client.get(
            "/api/admin/claims/1",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


def test_admin_approves_claim(client):
    with client.application.app_context():
        admin = create_user(
            "admin-approve@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-approve@mail.jiit.ac.in")
        claimant = create_user("claimant-approve@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/claims/{claim.id}/decision",
            json={
                "status": "approved",
                "admin_remarks": "Ownership verified successfully."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["claim"]["status"] == "approved"
        assert response.json["claim"]["admin_remarks"] == (
            "Ownership verified successfully."
        )

        db.session.refresh(item)
        assert item.status == "claimed"


def test_admin_rejects_claim(client):
    with client.application.app_context():
        admin = create_user(
            "admin-reject@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-reject@mail.jiit.ac.in")
        claimant = create_user("claimant-reject@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/claims/{claim.id}/decision",
            json={
                "status": "rejected",
                "admin_remarks": "The submitted evidence was insufficient."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["claim"]["status"] == "rejected"

        db.session.refresh(item)
        assert item.status == "active"


def test_admin_decision_rejects_invalid_status(client):
    with client.application.app_context():
        admin = create_user(
            "admin-invalid-decision@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-invalid-decision@mail.jiit.ac.in")
        claimant = create_user("claimant-invalid-decision@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/claims/{claim.id}/decision",
            json={
                "status": "pending",
                "admin_remarks": "Still reviewing."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400


def test_admin_decision_requires_remarks(client):
    with client.application.app_context():
        admin = create_user(
            "admin-no-remarks@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-no-remarks@mail.jiit.ac.in")
        claimant = create_user("claimant-no-remarks@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/claims/{claim.id}/decision",
            json={"status": "approved"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400
        db.session.refresh(claim)
        assert claim.status == "pending"


def test_approval_rejects_other_pending_claims(client):
    with client.application.app_context():
        admin = create_user(
            "admin-multiple@mail.jiit.ac.in",
            is_admin=True
        )
        reporter = create_user("reporter-multiple@mail.jiit.ac.in")
        claimant_one = create_user("claimant-one@mail.jiit.ac.in")
        claimant_two = create_user("claimant-two@mail.jiit.ac.in")

        item = create_item(reporter)
        first_claim = create_claim(claimant_one, item)
        second_claim = create_claim(claimant_two, item)
        token = create_token(admin)

        response = client.patch(
            f"/api/admin/claims/{first_claim.id}/decision",
            json={
                "status": "approved",
                "admin_remarks": "Ownership verified."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        db.session.refresh(second_claim)
        assert second_claim.status == "rejected"
        assert second_claim.admin_remarks == (
            "Another ownership claim was approved for this item."
        )


def test_only_admin_can_decide_claim(client):
    with client.application.app_context():
        student = create_user("student-decision@mail.jiit.ac.in")
        reporter = create_user("reporter-decision@mail.jiit.ac.in")
        claimant = create_user("claimant-decision@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(student)

        response = client.patch(
            f"/api/admin/claims/{claim.id}/decision",
            json={
                "status": "approved",
                "admin_remarks": "Ownership verified."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403

