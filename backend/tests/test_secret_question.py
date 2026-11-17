from datetime import date, datetime, timedelta, timezone

import jwt

from app import db
from config import TestConfig
from models.user import User
from models.item import Item

from models.item_secret import SecretVerification


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


def set_question(client, finder, item, answer="Blue Strap"):
    return client.put(
        f"/api/items/{item.id}/secret-question",
        json={"question": "What colour is the strap?", "answer": answer},
        headers=auth(finder)
    )


def test_finder_sets_secret_question(client):
    with client.application.app_context():
        finder = create_user("finder-sq@mail.jiit.ac.in")
        item = create_item(finder)

        response = set_question(client, finder, item)

        assert response.status_code == 200
        assert response.get_json()["question"] == "What colour is the strap?"


def test_lost_item_cannot_have_secret_question(client):
    with client.application.app_context():
        owner = create_user("owner-sq@mail.jiit.ac.in")
        item = create_item(owner, item_type="lost")

        assert set_question(client, owner, item).status_code == 400


def test_only_reporter_can_set_secret_question(client):
    with client.application.app_context():
        finder = create_user("finder2-sq@mail.jiit.ac.in")
        other = create_user("other-sq@mail.jiit.ac.in")
        item = create_item(finder)

        assert set_question(client, other, item).status_code == 404


def test_question_is_visible_but_answer_is_not(client):
    with client.application.app_context():
        finder = create_user("finder3-sq@mail.jiit.ac.in")
        claimant = create_user("claimant3-sq@mail.jiit.ac.in")
        item = create_item(finder)
        set_question(client, finder, item)

        response = client.get(
            f"/api/items/{item.id}/secret-question",
            headers=auth(claimant)
        )

        body = response.get_json()
        assert body["question"] == "What colour is the strap?"
        assert "answer" not in body
        assert "answer_hash" not in body


def test_correct_answer_is_case_and_space_insensitive(client):
    with client.application.app_context():
        finder = create_user("finder4-sq@mail.jiit.ac.in")
        claimant = create_user("claimant4-sq@mail.jiit.ac.in")
        item = create_item(finder)
        set_question(client, finder, item)

        response = client.post(
            f"/api/items/{item.id}/secret-question/verify",
            json={"answer": "  blue   STRAP "},
            headers=auth(claimant)
        )

        assert response.status_code == 200
        assert response.get_json()["verified"] is True


def test_three_wrong_answers_lock_the_user(client):
    with client.application.app_context():
        finder = create_user("finder5-sq@mail.jiit.ac.in")
        claimant = create_user("claimant5-sq@mail.jiit.ac.in")
        item = create_item(finder)
        set_question(client, finder, item)

        for expected_remaining in (2, 1, 0):
            response = client.post(
                f"/api/items/{item.id}/secret-question/verify",
                json={"answer": "red"},
                headers=auth(claimant)
            )
            assert response.status_code == 400
            assert response.get_json()["attempts_remaining"] == expected_remaining

        locked = client.post(
            f"/api/items/{item.id}/secret-question/verify",
            json={"answer": "Blue Strap"},
            headers=auth(claimant)
        )

        assert locked.status_code == 429


def test_claim_requires_verified_secret_answer(client):
    with client.application.app_context():
        finder = create_user("finder6-sq@mail.jiit.ac.in")
        claimant = create_user("claimant6-sq@mail.jiit.ac.in")
        item = create_item(finder)
        set_question(client, finder, item)

        payload = {"ownership_details": "It is my wallet."}

        blocked = client.post(
            f"/api/items/{item.id}/claims",
            json=payload,
            headers=auth(claimant)
        )
        assert blocked.status_code == 403

        client.post(
            f"/api/items/{item.id}/secret-question/verify",
            json={"answer": "blue strap"},
            headers=auth(claimant)
        )

        allowed = client.post(
            f"/api/items/{item.id}/claims",
            json=payload,
            headers=auth(claimant)
        )
        assert allowed.status_code == 201


def test_item_without_secret_question_can_still_be_claimed(client):
    with client.application.app_context():
        finder = create_user("finder7-sq@mail.jiit.ac.in")
        claimant = create_user("claimant7-sq@mail.jiit.ac.in")
        item = create_item(finder)

        response = client.post(
            f"/api/items/{item.id}/claims",
            json={"ownership_details": "It is my wallet."},
            headers=auth(claimant)
        )

        assert response.status_code == 201


def test_changing_answer_resets_verification(client):
    with client.application.app_context():
        finder = create_user("finder8-sq@mail.jiit.ac.in")
        claimant = create_user("claimant8-sq@mail.jiit.ac.in")
        item = create_item(finder)
        set_question(client, finder, item)

        client.post(
            f"/api/items/{item.id}/secret-question/verify",
            json={"answer": "blue strap"},
            headers=auth(claimant)
        )
        set_question(client, finder, item, answer="green")

        assert SecretVerification.query.filter_by(item_id=item.id).count() == 0
