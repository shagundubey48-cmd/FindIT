
from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item
from models.handover import Handover


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


def create_handover(reporter, recipient, admin):
    item = Item(
        user_id=reporter.id,
        title="Black Wallet",
        description="Black leather wallet",
        category="Accessories",
        campus="JIIT Noida",
        location="Library",
        item_type="found",
        item_date=date.today(),
        status="claimed"
    )
    db.session.add(item)
    db.session.commit()

    handover = Handover(
        claim_id=1,
        item_id=item.id,
        handed_over_by=admin.id,
        received_by=recipient.id,
        handover_notes="Item handed over.",
        handed_over_at=datetime.now(timezone.utc)
    )

    # Create a claim first because handovers reference an existing claim.
    from models.claim import Claim

    claim = Claim(
        claimant_id=recipient.id,
        item_id=item.id,
        ownership_details="My wallet has my initials.",
        status="approved"
    )
    db.session.add(claim)
    db.session.commit()

    handover.claim_id = claim.id
    db.session.add(handover)
    db.session.commit()

    return handover


def create_token(user):
    return jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        TestConfig.SECRET_KEY,
        algorithm="HS256"
    )


def test_recipient_can_submit_feedback(client):
    with client.application.app_context():
        reporter = create_user("reporter-feedback@mail.jiit.ac.in")
        recipient = create_user("recipient-feedback@mail.jiit.ac.in")
        admin = create_user("admin-feedback@mail.jiit.ac.in", True)

        handover = create_handover(reporter, recipient, admin)
        token = create_token(recipient)

        response = client.post(
            f"/api/handovers/{handover.id}/feedback",
            json={
                "rating": 5,
                "comment": "Very smooth recovery experience."
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        assert response.json["feedback"]["rating"] == 5
        assert response.json["feedback"]["comment"] == (
            "Very smooth recovery experience."
        )


def test_feedback_comment_is_optional(client):
    with client.application.app_context():
        reporter = create_user("reporter-optional@mail.jiit.ac.in")
        recipient = create_user("recipient-optional@mail.jiit.ac.in")
        admin = create_user("admin-optional@mail.jiit.ac.in", True)

        handover = create_handover(reporter, recipient, admin)
        token = create_token(recipient)

        response = client.post(
            f"/api/handovers/{handover.id}/feedback",
            json={"rating": 4},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        assert response.json["feedback"]["comment"] is None


def test_feedback_rejects_invalid_rating(client):
    with client.application.app_context():
        reporter = create_user("reporter-rating@mail.jiit.ac.in")
        recipient = create_user("recipient-rating@mail.jiit.ac.in")
        admin = create_user("admin-rating@mail.jiit.ac.in", True)

        handover = create_handover(reporter, recipient, admin)
        token = create_token(recipient)

        response = client.post(
            f"/api/handovers/{handover.id}/feedback",
            json={"rating": 6},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400


def test_only_recipient_can_submit_feedback(client):
    with client.application.app_context():
        reporter = create_user("reporter-access@mail.jiit.ac.in")
        recipient = create_user("recipient-access@mail.jiit.ac.in")
        admin = create_user("admin-access@mail.jiit.ac.in", True)

        handover = create_handover(reporter, recipient, admin)
        token = create_token(reporter)

        response = client.post(
            f"/api/handovers/{handover.id}/feedback",
            json={"rating": 5},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


def test_duplicate_feedback_is_rejected(client):
    with client.application.app_context():
        reporter = create_user("reporter-duplicate-feedback@mail.jiit.ac.in")
        recipient = create_user("recipient-duplicate-feedback@mail.jiit.ac.in")
        admin = create_user("admin-duplicate-feedback@mail.jiit.ac.in", True)

        handover = create_handover(reporter, recipient, admin)
        token = create_token(recipient)
        headers = {"Authorization": f"Bearer {token}"}

        first = client.post(
            f"/api/handovers/{handover.id}/feedback",
            json={"rating": 5},
            headers=headers
        )

        second = client.post(
            f"/api/handovers/{handover.id}/feedback",
            json={"rating": 4},
            headers=headers
        )

        assert first.status_code == 201
        assert second.status_code == 409


def test_user_can_view_own_feedback(client):
    with client.application.app_context():
        reporter = create_user("reporter-view@mail.jiit.ac.in")
        recipient = create_user("recipient-view@mail.jiit.ac.in")
        admin = create_user("admin-view@mail.jiit.ac.in", True)

        handover = create_handover(reporter, recipient, admin)
        token = create_token(recipient)

        client.post(
            f"/api/handovers/{handover.id}/feedback",
            json={"rating": 4, "comment": "Good experience."},
            headers={"Authorization": f"Bearer {token}"}
        )

        response = client.get(
            "/api/feedback/my",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1


def test_admin_can_view_all_feedback(client):
    with client.application.app_context():
        reporter = create_user("reporter-admin-view@mail.jiit.ac.in")
        recipient = create_user("recipient-admin-view@mail.jiit.ac.in")
        admin = create_user("admin-view-all@mail.jiit.ac.in", True)

        handover = create_handover(reporter, recipient, admin)
        recipient_token = create_token(recipient)

        client.post(
            f"/api/handovers/{handover.id}/feedback",
            json={"rating": 5},
            headers={"Authorization": f"Bearer {recipient_token}"}
        )

        admin_token = create_token(admin)

        response = client.get(
            "/api/admin/feedback",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json["count"] == 1

