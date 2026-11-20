from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item



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


from models.claim import Claim


def old_item(user, days_old, **kwargs):
    item = create_item(user, **kwargs)
        item.created_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days_old, minutes=1)
    db.session.commit()
    return item


def test_lists_only_old_active_found_items(client):
    with client.application.app_context():
        admin = create_user("admin-unc@mail.jiit.ac.in", True)
        reporter = create_user("reporter-unc@mail.jiit.ac.in")

        old = old_item(reporter, 45)
        old_item(reporter, 5)                         # too recent
        old_item(reporter, 45, item_type="lost")      # lost, not found
        old_item(reporter, 45, status="claimed")      # already claimed

        response = client.get(
            "/api/admin/unclaimed-items?days=30",
            headers=auth(admin)
        )

        body = response.get_json()
        assert response.status_code == 200
        assert body["count"] == 1
        assert body["items"][0]["id"] == old.id
        assert body["items"][0]["age_days"] >= 45


def test_item_with_pending_claim_is_not_unclaimed(client):
    with client.application.app_context():
        admin = create_user("admin2-unc@mail.jiit.ac.in", True)
        reporter = create_user("reporter2-unc@mail.jiit.ac.in")
        claimant = create_user("claimant2-unc@mail.jiit.ac.in")

        item = old_item(reporter, 60)
        db.session.add(Claim(
            claimant_id=claimant.id,
            item_id=item.id,
            ownership_details="Mine",
            status="pending"
        ))
        db.session.commit()

        response = client.get("/api/admin/unclaimed-items", headers=auth(admin))

        assert response.get_json()["count"] == 0


def test_invalid_days_value(client):
    with client.application.app_context():
        admin = create_user("admin3-unc@mail.jiit.ac.in", True)

        assert client.get(
            "/api/admin/unclaimed-items?days=abc", headers=auth(admin)
        ).status_code == 400
        assert client.get(
            "/api/admin/unclaimed-items?days=0", headers=auth(admin)
        ).status_code == 400


def test_students_cannot_access_unclaimed_items(client):
    with client.application.app_context():
        student = create_user("student-unc@mail.jiit.ac.in")

        assert client.get(
            "/api/admin/unclaimed-items", headers=auth(student)
        ).status_code == 403


def test_admin_can_archive_donate_and_dispose(client):
    with client.application.app_context():
        admin = create_user("admin4-unc@mail.jiit.ac.in", True)
        reporter = create_user("reporter4-unc@mail.jiit.ac.in")

        for action, status in (
            ("archive", "archived"),
            ("donate", "donated"),
            ("dispose", "disposed")
        ):
            item = old_item(reporter, 40)

            response = client.post(
                f"/api/admin/unclaimed-items/{item.id}/action",
                json={"action": action, "admin_remarks": "Held for 40 days."},
                headers=auth(admin)
            )

            assert response.status_code == 200
            assert response.get_json()["item"]["status"] == status


def test_action_validation(client):
    with client.application.app_context():
        admin = create_user("admin5-unc@mail.jiit.ac.in", True)
        reporter = create_user("reporter5-unc@mail.jiit.ac.in")
        item = old_item(reporter, 40)
        url = f"/api/admin/unclaimed-items/{item.id}/action"

        bad_action = client.post(
            url, json={"action": "sell", "admin_remarks": "x"},
            headers=auth(admin)
        )
        no_remarks = client.post(
            url, json={"action": "archive"}, headers=auth(admin)
        )

        assert bad_action.status_code == 400
        assert no_remarks.status_code == 400


def test_cannot_process_item_with_pending_claim_or_wrong_status(client):
    with client.application.app_context():
        admin = create_user("admin6-unc@mail.jiit.ac.in", True)
        reporter = create_user("reporter6-unc@mail.jiit.ac.in")
        claimant = create_user("claimant6-unc@mail.jiit.ac.in")

        claimed = old_item(reporter, 40, status="claimed")
        pending = old_item(reporter, 40)
        db.session.add(Claim(
            claimant_id=claimant.id,
            item_id=pending.id,
            ownership_details="Mine",
            status="pending"
        ))
        db.session.commit()

        payload = {"action": "archive", "admin_remarks": "Cleanup"}

        for target in (claimed, pending):
            response = client.post(
                f"/api/admin/unclaimed-items/{target.id}/action",
                json=payload,
                headers=auth(admin)
            )
            assert response.status_code == 409


def test_processed_items_leave_public_listing(client):
    with client.application.app_context():
        admin = create_user("admin7-unc@mail.jiit.ac.in", True)
        reporter = create_user("reporter7-unc@mail.jiit.ac.in")
        item = old_item(reporter, 40)

        client.post(
            f"/api/admin/unclaimed-items/{item.id}/action",
            json={"action": "archive", "admin_remarks": "Cleanup"},
            headers=auth(admin)
        )

        listing = client.get("/api/items", headers=auth(reporter)).get_json()

        assert listing["count"] == 0
