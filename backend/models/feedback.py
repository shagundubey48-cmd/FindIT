
from datetime import datetime, timezone

from app import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)

    handover_id = db.Column(
        db.Integer,
        db.ForeignKey("handovers.id"),
        nullable=False,
        unique=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    rating = db.Column(db.Integer, nullable=False)

    comment = db.Column(db.String(1000), nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    handover = db.relationship("Handover", backref="feedback", uselist=False)
    user = db.relationship("User", backref="submitted_feedback")

