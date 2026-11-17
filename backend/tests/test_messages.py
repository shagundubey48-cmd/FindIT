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


from models.conversation import Conversation


def start(client, user, item, body="Hi, I think this is mine."):
    return client.post(
        f"/api/items/{item.id}/conversations",
        json={"body": body},
        headers=auth(user)
    )


def test_user_can_start_anonymous_conversation(client):
    with client.application.app_context():
        reporter = create_user("reporter-msg@mail.jiit.ac.in", name="Real Reporter")
        asker = create_user("asker-msg@mail.jiit.ac.in", name="Real Asker")
        item = create_item(reporter)

        response = start(client, asker, item)

        assert response.status_code == 201
        conversation = response.get_json()["conversation"]
        assert conversation["other_party"] == "Item reporter"
        assert "Real Reporter" not in response.get_data(as_text=True)


def test_cannot_message_own_item(client):
    with client.application.app_context():
        reporter = create_user("reporter2-msg@mail.jiit.ac.in")
        item = create_item(reporter)

        assert start(client, reporter, item).status_code == 403


def test_cannot_message_inactive_item(client):
    with client.application.app_context():
        reporter = create_user("reporter3-msg@mail.jiit.ac.in")
        asker = create_user("asker3-msg@mail.jiit.ac.in")
        item = create_item(reporter, status="withdrawn")

        assert start(client, asker, item).status_code == 404


def test_empty_and_long_messages_are_rejected(client):
    with client.application.app_context():
        reporter = create_user("reporter4-msg@mail.jiit.ac.in")
        asker = create_user("asker4-msg@mail.jiit.ac.in")
        item = create_item(reporter)

        assert start(client, asker, item, body="   ").status_code == 400
        assert start(client, asker, item, body="x" * 1001).status_code == 400


def test_second_start_reuses_the_same_conversation(client):
    with client.application.app_context():
        reporter = create_user("reporter5-msg@mail.jiit.ac.in")
        asker = create_user("asker5-msg@mail.jiit.ac.in")
        item = create_item(reporter)

        first = start(client, asker, item)
        second = start(client, asker, item, body="Any update?")

        assert first.status_code == 201
        assert second.status_code == 200
        assert Conversation.query.count() == 1


def test_reporter_replies_and_asker_sees_it_anonymously(client):
    with client.application.app_context():
        reporter = create_user("reporter6-msg@mail.jiit.ac.in", name="Real Reporter")
        asker = create_user("asker6-msg@mail.jiit.ac.in", name="Real Asker")
        item = create_item(reporter)

        conversation_id = start(client, asker, item).get_json()["conversation"]["id"]

        reply = client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"body": "What colour is it?"},
            headers=auth(reporter)
        )
        assert reply.status_code == 201

        thread = client.get(
            f"/api/conversations/{conversation_id}/messages",
            headers=auth(asker)
        )

        body = thread.get_json()
        assert body["count"] == 2
        assert body["conversation"]["other_party"] == "Item reporter"
        assert "Real Reporter" not in thread.get_data(as_text=True)
        assert "reporter6-msg" not in thread.get_data(as_text=True)

        reporter_view = client.get(
            f"/api/conversations/{conversation_id}/messages",
            headers=auth(reporter)
        )
        assert reporter_view.get_json()["conversation"]["other_party"] == "Anonymous user"


def test_outsider_cannot_read_or_post(client):
    with client.application.app_context():
        reporter = create_user("reporter7-msg@mail.jiit.ac.in")
        asker = create_user("asker7-msg@mail.jiit.ac.in")
        outsider = create_user("outsider-msg@mail.jiit.ac.in")
        item = create_item(reporter)

        conversation_id = start(client, asker, item).get_json()["conversation"]["id"]

        read = client.get(
            f"/api/conversations/{conversation_id}/messages",
            headers=auth(outsider)
        )
        post = client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"body": "hello"},
            headers=auth(outsider)
        )

        assert read.status_code == 404
        assert post.status_code == 404


def test_unread_counts_and_mark_as_read(client):
    with client.application.app_context():
        reporter = create_user("reporter8-msg@mail.jiit.ac.in")
        asker = create_user("asker8-msg@mail.jiit.ac.in")
        item = create_item(reporter)

        conversation_id = start(client, asker, item).get_json()["conversation"]["id"]

        inbox = client.get("/api/conversations", headers=auth(reporter)).get_json()
        assert inbox["unread_count"] == 1

        client.get(
            f"/api/conversations/{conversation_id}/messages",
            headers=auth(reporter)
        )

        inbox = client.get("/api/conversations", headers=auth(reporter)).get_json()
        assert inbox["unread_count"] == 0

        # The sender's own message never counts as unread for them.
        sender_inbox = client.get("/api/conversations", headers=auth(asker)).get_json()
        assert sender_inbox["unread_count"] == 0


def test_cannot_reply_after_item_is_closed(client):
    with client.application.app_context():
        reporter = create_user("reporter9-msg@mail.jiit.ac.in")
        asker = create_user("asker9-msg@mail.jiit.ac.in")
        item = create_item(reporter)

        conversation_id = start(client, asker, item).get_json()["conversation"]["id"]

        item.status = "claimed"
        db.session.commit()

        response = client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"body": "Still there?"},
            headers=auth(asker)
        )

        assert response.status_code == 400
