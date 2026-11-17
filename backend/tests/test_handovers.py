
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


def create_item(user, status="claimed"):
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


def create_claim(user, item, status="approved"):
    claim = Claim(
        claimant_id=user.id,
        item_id=item.id,
        ownership_details="The wallet has my initials inside.",
        status=status
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


def test_admin_records_handover(client):
    with client.application.app_context():
        admin = create_user("admin-handover@mail.jiit.ac.in", True)
        reporter = create_user("reporter-handover@mail.jiit.ac.in")
        claimant = create_user("claimant-handover@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(admin)

        response = client.post(
            f"/api/admin/claims/{claim.id}/handover",
            json={"handover_notes": "Wallet handed over successfully."},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        assert response.json["handover"]["item_id"] == item.id
        assert response.json["handover"]["received_by"] == claimant.id
        assert response.json["handover"]["handover_notes"] == (
            "Wallet handed over successfully."
        )


def test_non_admin_cannot_record_handover(client):
    with client.application.app_context():
        student = create_user("student-handover@mail.jiit.ac.in")
        reporter = create_user("reporter-nonadmin@mail.jiit.ac.in")
        claimant = create_user("claimant-nonadmin@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(student)

        response = client.post(
            f"/api/admin/claims/{claim.id}/handover",
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


def test_pending_claim_cannot_be_handed_over(client):
    with client.application.app_context():
        admin = create_user("admin-pending@mail.jiit.ac.in", True)
        reporter = create_user("reporter-pending@mail.jiit.ac.in")
        claimant = create_user("claimant-pending@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item, status="pending")
        token = create_token(admin)

        response = client.post(
            f"/api/admin/claims/{claim.id}/handover",
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400


def test_duplicate_handover_is_rejected(client):
    with client.application.app_context():
        admin = create_user("admin-duplicate@mail.jiit.ac.in", True)
        reporter = create_user("reporter-duplicate@mail.jiit.ac.in")
        claimant = create_user("claimant-duplicate@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(admin)

        first_response = client.post(
            f"/api/admin/claims/{claim.id}/handover",
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )

        second_response = client.post(
            f"/api/admin/claims/{claim.id}/handover",
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409


def test_reporter_can_view_handover_history(client):
    with client.application.app_context():
        admin = create_user("admin-history@mail.jiit.ac.in", True)
        reporter = create_user("reporter-history@mail.jiit.ac.in")
        claimant = create_user("claimant-history@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        admin_token = create_token(admin)

        client.post(
            f"/api/admin/claims/{claim.id}/handover",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        reporter_token = create_token(reporter)

        response = client.get(
            f"/api/items/{item.id}/handover-history",
            headers={"Authorization": f"Bearer {reporter_token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["history"][0]["claim_id"] == claim.id


def test_unrelated_student_cannot_view_handover_history(client):
    with client.application.app_context():
        admin = create_user("admin-private@mail.jiit.ac.in", True)
        reporter = create_user("reporter-private@mail.jiit.ac.in")
        claimant = create_user("claimant-private@mail.jiit.ac.in")
        student = create_user("student-private@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        admin_token = create_token(admin)

        client.post(
            f"/api/admin/claims/{claim.id}/handover",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        student_token = create_token(student)

        response = client.get(
            f"/api/items/{item.id}/handover-history",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        assert response.status_code == 403


def test_user_can_view_their_own_handovers(client):
    with client.application.app_context():
        admin = create_user("admin-myhistory@mail.jiit.ac.in", True)
        reporter = create_user("reporter-myhistory@mail.jiit.ac.in")
        claimant = create_user("claimant-myhistory@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        admin_token = create_token(admin)

        client.post(
            f"/api/admin/claims/{claim.id}/handover",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        claimant_token = create_token(claimant)

        response = client.get(
            "/api/handovers/my",
            headers={"Authorization": f"Bearer {claimant_token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1

