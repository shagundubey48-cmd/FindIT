
from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from app import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False
    )

    matched_item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False
    )

    message = db.Column(db.String(300), nullable=False)

    is_read = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "item_id",
            "matched_item_id",
            name="unique_user_item_match_notification"
        ),
    )

    user = db.relationship("User", backref="notifications")
    item = db.relationship("Item", foreign_keys=[item_id])
    matched_item = db.relationship("Item", foreign_keys=[matched_item_id])

