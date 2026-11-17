
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


def test_submit_claim_evidence_success(client):
    with client.application.app_context():
        reporter = create_user("reporter-proof@mail.jiit.ac.in")
        claimant = create_user("claimant-proof@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(claimant)

        response = client.put(
            f"/api/claims/{claim.id}/evidence",
            json={
                "proof_type": "identifying_mark",
                "proof_details": "There is a small scratch near the zip."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["claim"]["proof_type"] == "identifying_mark"
        assert "scratch" in response.json["claim"]["proof_details"]


def test_submit_claim_evidence_rejects_invalid_type(client):
    with client.application.app_context():
        reporter = create_user("reporter-invalid-proof@mail.jiit.ac.in")
        claimant = create_user("claimant-invalid-proof@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(claimant)

        response = client.put(
            f"/api/claims/{claim.id}/evidence",
            json={
                "proof_type": "invalid_type",
                "proof_details": "Some proof."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400


def test_submit_claim_evidence_requires_details(client):
    with client.application.app_context():
        reporter = create_user("reporter-empty-proof@mail.jiit.ac.in")
        claimant = create_user("claimant-empty-proof@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(claimant)

        response = client.put(
            f"/api/claims/{claim.id}/evidence",
            json={
                "proof_type": "serial_number",
                "proof_details": "   "
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400


def test_claimant_can_update_evidence(client):
    with client.application.app_context():
        reporter = create_user("reporter-update-proof@mail.jiit.ac.in")
        claimant = create_user("claimant-update-proof@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(claimant)

        payload = {
            "proof_type": "other",
            "proof_details": "First proof details."
        }

        client.put(
            f"/api/claims/{claim.id}/evidence",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        response = client.put(
            f"/api/claims/{claim.id}/evidence",
            json={
                "proof_type": "purchase_proof",
                "proof_details": "I have the original purchase receipt."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["claim"]["proof_type"] == "purchase_proof"


def test_user_cannot_submit_evidence_for_another_claim(client):
    with client.application.app_context():
        reporter = create_user("reporter-owner-proof@mail.jiit.ac.in")
        claimant = create_user("claimant-owner-proof@mail.jiit.ac.in")
        another_user = create_user("another-owner-proof@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)
        token = create_token(another_user)

        response = client.put(
            f"/api/claims/{claim.id}/evidence",
            json={
                "proof_type": "other",
                "proof_details": "This is my proof."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


def test_get_claim_details_includes_evidence(client):
    with client.application.app_context():
        reporter = create_user("reporter-details-proof@mail.jiit.ac.in")
        claimant = create_user("claimant-details-proof@mail.jiit.ac.in")

        item = create_item(reporter)
        claim = create_claim(claimant, item)

        claim.proof_type = "serial_number"
        claim.proof_details = "Serial number is ABC123."
        db.session.commit()

        token = create_token(claimant)

        response = client.get(
            f"/api/claims/{claim.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["claim"]["proof_type"] == "serial_number"
        assert response.json["claim"]["proof_details"] == "Serial number is ABC123."


def test_evidence_requires_authentication(client):
    response = client.put(
        "/api/claims/1/evidence",
        json={
            "proof_type": "other",
            "proof_details": "Some proof."
        }
    )

    assert response.status_code == 401

