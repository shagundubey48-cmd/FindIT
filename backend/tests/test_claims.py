
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


def create_item(user, item_type="found", status="active"):
    item = Item(
        user_id=user.id,
        title="Black Wallet",
        description="Black leather wallet",
        category="Accessories",
        campus="JIIT Noida",
        location="Library",
        item_type=item_type,
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


def test_submit_claim_success(client):
    with client.application.app_context():
        reporter = create_user("reporter@mail.jiit.ac.in")
        claimant = create_user("claimant@mail.jiit.ac.in")
        item = create_item(reporter)

        token = create_token(claimant)

        response = client.post(
            f"/api/items/{item.id}/claims",
            json={
                "ownership_details": "My initials are engraved inside the wallet."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        assert response.json["claim"]["status"] == "pending"
        assert Claim.query.count() == 1


def test_claim_requires_ownership_details(client):
    with client.application.app_context():
        reporter = create_user("reporter-empty@mail.jiit.ac.in")
        claimant = create_user("claimant-empty@mail.jiit.ac.in")
        item = create_item(reporter)

        token = create_token(claimant)

        response = client.post(
            f"/api/items/{item.id}/claims",
            json={"ownership_details": "   "},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400
        assert Claim.query.count() == 0


def test_claim_rejects_non_found_item(client):
    with client.application.app_context():
        reporter = create_user("reporter-lost@mail.jiit.ac.in")
        claimant = create_user("claimant-lost@mail.jiit.ac.in")
        item = create_item(reporter, item_type="lost")

        token = create_token(claimant)

        response = client.post(
            f"/api/items/{item.id}/claims",
            json={"ownership_details": "This belongs to me."},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400


def test_user_cannot_claim_own_item(client):
    with client.application.app_context():
        user = create_user("own-item@mail.jiit.ac.in")
        item = create_item(user)

        token = create_token(user)

        response = client.post(
            f"/api/items/{item.id}/claims",
            json={"ownership_details": "This belongs to me."},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


def test_claim_rejects_inactive_item(client):
    with client.application.app_context():
        reporter = create_user("reporter-inactive@mail.jiit.ac.in")
        claimant = create_user("claimant-inactive@mail.jiit.ac.in")
        item = create_item(reporter, status="withdrawn")

        token = create_token(claimant)

        response = client.post(
            f"/api/items/{item.id}/claims",
            json={"ownership_details": "This belongs to me."},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400


def test_duplicate_pending_claim_is_rejected(client):
    with client.application.app_context():
        reporter = create_user("reporter-duplicate@mail.jiit.ac.in")
        claimant = create_user("claimant-duplicate@mail.jiit.ac.in")
        item = create_item(reporter)

        token = create_token(claimant)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"ownership_details": "My initials are engraved inside."}

        first_response = client.post(
            f"/api/items/{item.id}/claims",
            json=payload,
            headers=headers
        )

        second_response = client.post(
            f"/api/items/{item.id}/claims",
            json=payload,
            headers=headers
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert Claim.query.count() == 1


def test_get_my_claims(client):
    with client.application.app_context():
        reporter = create_user("reporter-list@mail.jiit.ac.in")
        claimant = create_user("claimant-list@mail.jiit.ac.in")
        item = create_item(reporter)

        token = create_token(claimant)

        client.post(
            f"/api/items/{item.id}/claims",
            json={"ownership_details": "My initials are engraved inside."},
            headers={"Authorization": f"Bearer {token}"}
        )

        response = client.get(
            "/api/claims",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["claims"][0]["status"] == "pending"


def test_claim_endpoints_require_authentication(client):
    response = client.get("/api/claims")

    assert response.status_code == 401


def test_claim_item_not_found(client):
    with client.application.app_context():
        claimant = create_user("claimant-missing@mail.jiit.ac.in")
        token = create_token(claimant)

        response = client.post(
            "/api/items/99999/claims",
            json={"ownership_details": "This belongs to me."},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

