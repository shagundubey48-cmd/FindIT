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
from models.handover import Handover
from models.feedback import Feedback


def record_recovery(admin, reporter, claimant, category="Accessories"):
    item = create_item(reporter, status="claimed", category=category)
    claim = Claim(
        claimant_id=claimant.id,
        item_id=item.id,
        ownership_details="Mine",
        status="approved"
    )
    db.session.add(claim)
    db.session.commit()

    handover = Handover(
        claim_id=claim.id,
        item_id=item.id,
        handed_over_by=admin.id,
        received_by=claimant.id,
        handed_over_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.session.add(handover)
    db.session.commit()
    return handover


def test_empty_database_returns_zeroes(client):
    with client.application.app_context():
        admin = create_user("admin-stat@mail.jiit.ac.in", True)

        response = client.get("/api/admin/statistics", headers=auth(admin))
        body = response.get_json()

        assert response.status_code == 200
        assert body["recovery_rate"] == 0.0
        assert body["average_recovery_days"] is None
        assert len(body["monthly_trend"]) == 6
        assert body["feedback"]["average_rating"] is None


def test_recovery_rate_and_claim_figures(client):
    with client.application.app_context():
        admin = create_user("admin2-stat@mail.jiit.ac.in", True)
        reporter = create_user("reporter2-stat@mail.jiit.ac.in")
        claimant = create_user("claimant2-stat@mail.jiit.ac.in")

        record_recovery(admin, reporter, claimant)
        create_item(reporter)                          # still unclaimed
        create_item(reporter, item_type="lost")

        rejected_target = create_item(reporter)
        db.session.add(Claim(
            claimant_id=claimant.id,
            item_id=rejected_target.id,
            ownership_details="Not mine",
            status="rejected"
        ))
        db.session.commit()

        body = client.get("/api/admin/statistics", headers=auth(admin)).get_json()

        assert body["total_found_reports"] == 3
        assert body["total_lost_reports"] == 1
        assert body["items_recovered"] == 1
        assert body["recovery_rate"] == 33.3
        assert body["claims"]["approved"] == 1
        assert body["claims"]["rejected"] == 1
        assert body["claims"]["approval_rate"] == 50.0
        assert body["average_recovery_days"] is not None


def test_category_breakdown_and_trend(client):
    with client.application.app_context():
        admin = create_user("admin3-stat@mail.jiit.ac.in", True)
        reporter = create_user("reporter3-stat@mail.jiit.ac.in")
        claimant = create_user("claimant3-stat@mail.jiit.ac.in")

        record_recovery(admin, reporter, claimant, category="Electronics")
        create_item(reporter, category="Electronics")

        body = client.get("/api/admin/statistics", headers=auth(admin)).get_json()

        electronics = next(
            c for c in body["by_category"] if c["category"] == "Electronics"
        )
        assert electronics["found"] == 2
        assert electronics["recovered"] == 1
        assert electronics["recovery_rate"] == 50.0

        this_month = body["monthly_trend"][-1]
        assert this_month["reports"] == 2
        assert this_month["recoveries"] == 1


def test_average_feedback_rating(client):
    with client.application.app_context():
        admin = create_user("admin4-stat@mail.jiit.ac.in", True)
        reporter = create_user("reporter4-stat@mail.jiit.ac.in")
        claimant = create_user("claimant4-stat@mail.jiit.ac.in")

        handover = record_recovery(admin, reporter, claimant)
        db.session.add(Feedback(
            handover_id=handover.id,
            user_id=claimant.id,
            rating=4
        ))
        db.session.commit()

        body = client.get("/api/admin/statistics", headers=auth(admin)).get_json()

        assert body["feedback"] == {"count": 1, "average_rating": 4.0}


def test_students_cannot_see_detailed_statistics(client):
    with client.application.app_context():
        student = create_user("student-stat@mail.jiit.ac.in")

        response = client.get("/api/admin/statistics", headers=auth(student))

        assert response.status_code == 403


def test_students_can_see_public_summary(client):
    with client.application.app_context():
        admin = create_user("admin5-stat@mail.jiit.ac.in", True)
        student = create_user("student2-stat@mail.jiit.ac.in")
        claimant = create_user("claimant5-stat@mail.jiit.ac.in")

        record_recovery(admin, student, claimant)

        response = client.get("/api/statistics/summary", headers=auth(student))
        body = response.get_json()

        assert response.status_code == 200
        assert body["items_recovered"] == 1
        assert "claims" not in body


def test_statistics_require_login(client):
    assert client.get("/api/statistics/summary").status_code == 401
