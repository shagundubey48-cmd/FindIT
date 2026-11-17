from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item

from models.claim import Claim
from models.handover import Handover


def create_user(email, is_admin=False, name="Test User"):
    user = User(
        name=name,
        email=email,
        password="test-password",
        is_verified=True,
        is_admin=is_admin
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_item(user, item_type="found", status="active", category="Accessories"):
    item = Item(
        user_id=user.id,
        title="Black Wallet",
        description="Black leather wallet",
        category=category,
        campus="JIIT Noida",
        location="Library",
        item_type=item_type,
        item_date=date.today(),
        status=status
    )
    db.session.add(item)
    db.session.commit()
    return item


def auth(user):
    token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        TestConfig.SECRET_KEY,
        algorithm="HS256"
    )
    return {"Authorization": f"Bearer {token}"}


def create_claim(user, item, status="approved"):
    claim = Claim(
        claimant_id=user.id,
        item_id=item.id,
        ownership_details="Initials inside.",
        status=status
    )
    db.session.add(claim)
    db.session.commit()
    return claim


def test_reporter_gets_item_qr_png(client):
    with client.application.app_context():
        reporter = create_user("reporter-qr@mail.jiit.ac.in")
        item = create_item(reporter)

        response = client.get(
            f"/api/items/{item.id}/qr",
            headers=auth(reporter)
        )

        assert response.status_code == 200
        assert response.mimetype == "image/png"
        assert response.data.startswith(b"\x89PNG")


def test_other_student_cannot_get_item_qr(client):
    with client.application.app_context():
        reporter = create_user("reporter2-qr@mail.jiit.ac.in")
        other = create_user("other-qr@mail.jiit.ac.in")
        item = create_item(reporter)

        response = client.get(
            f"/api/items/{item.id}/qr",
            headers=auth(other)
        )

        assert response.status_code == 403


def test_admin_can_get_item_qr(client):
    with client.application.app_context():
        reporter = create_user("reporter3-qr@mail.jiit.ac.in")
        admin = create_user("admin-qr@mail.jiit.ac.in", True)
        item = create_item(reporter)

        response = client.get(
            f"/api/items/{item.id}/qr",
            headers=auth(admin)
        )

        assert response.status_code == 200


def test_item_qr_for_missing_item(client):
    with client.application.app_context():
        user = create_user("user-qr@mail.jiit.ac.in")

        response = client.get("/api/items/9999/qr", headers=auth(user))

        assert response.status_code == 404


def test_handover_qr_requires_approved_claim(client):
    with client.application.app_context():
        reporter = create_user("reporter4-qr@mail.jiit.ac.in")
        claimant = create_user("claimant4-qr@mail.jiit.ac.in")
        item = create_item(reporter)
        claim = create_claim(claimant, item, status="pending")

        response = client.get(
            f"/api/claims/{claim.id}/handover-qr",
            headers=auth(claimant)
        )

        assert response.status_code == 400


def test_only_claimant_gets_handover_qr(client):
    with client.application.app_context():
        reporter = create_user("reporter5-qr@mail.jiit.ac.in")
        claimant = create_user("claimant5-qr@mail.jiit.ac.in")
        item = create_item(reporter, status="claimed")
        claim = create_claim(claimant, item)

        response = client.get(
            f"/api/claims/{claim.id}/handover-qr",
            headers=auth(reporter)
        )

        assert response.status_code == 404


def test_admin_verifies_handover_token(client):
    with client.application.app_context():
        from routes.qr_codes import handover_serializer

        admin = create_user("admin2-qr@mail.jiit.ac.in", True)
        reporter = create_user("reporter6-qr@mail.jiit.ac.in")
        claimant = create_user("claimant6-qr@mail.jiit.ac.in", name="Asha")
        item = create_item(reporter, status="claimed")
        claim = create_claim(claimant, item)

        token = handover_serializer().dumps({"claim_id": claim.id})

        response = client.post(
            "/api/admin/handover-qr/verify",
            json={"token": token},
            headers=auth(admin)
        )

        assert response.status_code == 200
        assert response.get_json()["claimant_name"] == "Asha"


def test_tampered_or_missing_token_is_rejected(client):
    with client.application.app_context():
        admin = create_user("admin3-qr@mail.jiit.ac.in", True)

        bad = client.post(
            "/api/admin/handover-qr/verify",
            json={"token": "not-a-real-token"},
            headers=auth(admin)
        )
        missing = client.post(
            "/api/admin/handover-qr/verify",
            json={},
            headers=auth(admin)
        )

        assert bad.status_code == 400
        assert missing.status_code == 400


def test_student_cannot_verify_handover_token(client):
    with client.application.app_context():
        student = create_user("student-qr@mail.jiit.ac.in")

        response = client.post(
            "/api/admin/handover-qr/verify",
            json={"token": "x"},
            headers=auth(student)
        )

        assert response.status_code == 403


def test_already_handed_over_claim_is_rejected(client):
    with client.application.app_context():
        from routes.qr_codes import handover_serializer

        admin = create_user("admin4-qr@mail.jiit.ac.in", True)
        reporter = create_user("reporter7-qr@mail.jiit.ac.in")
        claimant = create_user("claimant7-qr@mail.jiit.ac.in")
        item = create_item(reporter, status="claimed")
        claim = create_claim(claimant, item)

        db.session.add(Handover(
            claim_id=claim.id,
            item_id=item.id,
            handed_over_by=admin.id,
            received_by=claimant.id
        ))
        db.session.commit()

        response = client.post(
            "/api/admin/handover-qr/verify",
            json={"token": handover_serializer().dumps({"claim_id": claim.id})},
            headers=auth(admin)
        )

        assert response.status_code == 409
