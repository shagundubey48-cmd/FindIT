from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint

from app import db


class ItemSecret(db.Model):
    """Secret question set by the finder of a found item (US-16)."""

    __tablename__ = "item_secrets"

    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False,
        unique=True
    )

    question = db.Column(db.String(255), nullable=False)

    # The answer is never stored in plain text.
    answer_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    item = db.relationship("Item", backref=db.backref("secret", uselist=False))


class SecretVerification(db.Model):
    """Tracks a user's attempts at answering an item's secret question."""

    __tablename__ = "secret_verifications"

    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    failed_attempts = db.Column(db.Integer, nullable=False, default=0)
    verified_at = db.Column(db.DateTime, nullable=True)
    locked_until = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "user_id",
            name="unique_item_user_secret_verification"
        ),
    )
