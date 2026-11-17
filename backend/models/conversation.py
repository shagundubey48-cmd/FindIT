from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint

from app import db


class Conversation(db.Model):
    """An anonymous chat between an item's reporter and an interested user."""

    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False
    )

    # User who started the conversation.
    initiator_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # User who reported the item.
    reporter_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "initiator_id",
            name="unique_item_initiator_conversation"
        ),
    )

    item = db.relationship("Item", backref="conversations")
    messages = db.relationship(
        "Message",
        backref="conversation",
        order_by="Message.created_at, Message.id"
    )


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id"),
        nullable=False
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    body = db.Column(db.String(1000), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
