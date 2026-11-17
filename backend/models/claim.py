
from datetime import datetime, timezone

from app import db


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)

    claimant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False
    )

    ownership_details = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    claimant = db.relationship("User", backref="claims")
    item = db.relationship("Item", backref="claims")

