from flask import Blueprint, jsonify, request, g
from sqlalchemy import or_

from app import db
from models.item import Item
from models.conversation import Conversation, Message
from utils.auth_middleware import token_required


messages_bp = Blueprint("messages", __name__)

MAX_MESSAGE_LENGTH = 1000

REPORTER_ALIAS = "Item reporter"
OTHER_ALIAS = "Anonymous user"


def other_party_alias(conversation, user):
    """Name shown for the other side. Real identities are never exposed."""
    if user.id == conversation.reporter_id:
        return OTHER_ALIAS
    return REPORTER_ALIAS


def serialize_message(message, user):
    return {
        "id": message.id,
        "body": message.body,
        "is_mine": message.sender_id == user.id,
        "is_read": message.is_read,
        "created_at": message.created_at.isoformat()
    }


def serialize_conversation(conversation, user):
    messages = conversation.messages
    last_message = messages[-1] if messages else None

    unread_count = sum(
        1 for message in messages
        if message.sender_id != user.id and not message.is_read
    )

    return {
        "id": conversation.id,
        "item_id": conversation.item_id,
        "item_title": conversation.item.title,
        "other_party": other_party_alias(conversation, user),
        "unread_count": unread_count,
        "last_message": (
            serialize_message(last_message, user) if last_message else None
        ),
        "created_at": conversation.created_at.isoformat()
    }


def validate_body(data):
    body = data.get("body")

    if not isinstance(body, str) or not body.strip():
        return None, "Message cannot be empty"

    body = body.strip()

    if len(body) > MAX_MESSAGE_LENGTH:
        return None, (
            f"Message cannot exceed {MAX_MESSAGE_LENGTH} characters"
        )

    return body, None


def get_participant_conversation(conversation_id, user):
    """Return the conversation only if the user takes part in it."""
    return Conversation.query.filter(
        Conversation.id == conversation_id,
        or_(
            Conversation.initiator_id == user.id,
            Conversation.reporter_id == user.id
        )
    ).first()


@messages_bp.route("/items/<int:item_id>/conversations", methods=["POST"])
@token_required
def start_conversation(item_id):
    """Message the person who reported an item without revealing identity."""

    item = Item.query.filter_by(id=item_id, status="active").first()

    if not item:
        return jsonify({"message": "Item not found"}), 404

    if item.user_id == g.current_user.id:
        return jsonify({
            "message": "You cannot message yourself about your own item"
        }), 403

    data = request.get_json(silent=True) or {}
    body, error = validate_body(data)

    if error:
        return jsonify({"message": error}), 400

    conversation = Conversation.query.filter_by(
        item_id=item.id,
        initiator_id=g.current_user.id
    ).first()

    created = conversation is None

    if created:
        conversation = Conversation(
            item_id=item.id,
            initiator_id=g.current_user.id,
            reporter_id=item.user_id
        )
        db.session.add(conversation)
        db.session.flush()

    db.session.add(Message(
        conversation_id=conversation.id,
        sender_id=g.current_user.id,
        body=body
    ))
    db.session.commit()

    return jsonify({
        "message": "Message sent",
        "conversation": serialize_conversation(conversation, g.current_user)
    }), 201 if created else 200


@messages_bp.route("/conversations", methods=["GET"])
@token_required
def list_conversations():
    """List the logged-in user's anonymous conversations."""

    conversations = Conversation.query.filter(
        or_(
            Conversation.initiator_id == g.current_user.id,
            Conversation.reporter_id == g.current_user.id
        )
    ).all()

    results = [
        serialize_conversation(conversation, g.current_user)
        for conversation in conversations
    ]

    # Most recently active conversation first.
    results.sort(
        key=lambda c: (c["last_message"] or c)["created_at"],
        reverse=True
    )

    return jsonify({
        "count": len(results),
        "unread_count": sum(c["unread_count"] for c in results),
        "conversations": results
    }), 200


@messages_bp.route(
    "/conversations/<int:conversation_id>/messages",
    methods=["GET"]
)
@token_required
def get_messages(conversation_id):
    """Read a conversation. Messages from the other side become 'read'."""

    conversation = get_participant_conversation(
        conversation_id, g.current_user
    )

    if not conversation:
        return jsonify({"message": "Conversation not found"}), 404

    for message in conversation.messages:
        if message.sender_id != g.current_user.id and not message.is_read:
            message.is_read = True

    db.session.commit()

    return jsonify({
        "conversation": serialize_conversation(conversation, g.current_user),
        "count": len(conversation.messages),
        "messages": [
            serialize_message(message, g.current_user)
            for message in conversation.messages
        ]
    }), 200


@messages_bp.route(
    "/conversations/<int:conversation_id>/messages",
    methods=["POST"]
)
@token_required
def send_message(conversation_id):
    """Reply inside an existing conversation."""

    conversation = get_participant_conversation(
        conversation_id, g.current_user
    )

    if not conversation:
        return jsonify({"message": "Conversation not found"}), 404

    if conversation.item.status != "active":
        return jsonify({
            "message": "This item is no longer active"
        }), 400

    data = request.get_json(silent=True) or {}
    body, error = validate_body(data)

    if error:
        return jsonify({"message": error}), 400

    message = Message(
        conversation_id=conversation.id,
        sender_id=g.current_user.id,
        body=body
    )

    db.session.add(message)
    db.session.commit()

    return jsonify({
        "message": "Message sent",
        "data": serialize_message(message, g.current_user)
    }), 201
