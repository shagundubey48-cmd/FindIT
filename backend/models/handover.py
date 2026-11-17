
from datetime import datetime, timezone

from app import db


class Handover(db.Model):
    __tablename__ = "handovers"

    id = db.Column(db.Integer, primary_key=True)

    claim_id = db.Column(
        db.Integer,
        db.ForeignKey("claims.id"),
        nullable=False,
        unique=True
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False
    )

    handed_over_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    received_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    handover_notes = db.Column(db.Text, nullable=True)

    handed_over_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    claim = db.relationship("Claim", backref="handover", uselist=False)
    item = db.relationship("Item", backref="handovers")

    administrator = db.relationship(
        "User",
        foreign_keys=[handed_over_by]
    )

    recipient = db.relationship(
        "User",
        foreign_keys=[received_by]
    )

