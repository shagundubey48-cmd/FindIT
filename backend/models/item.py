
from datetime import datetime, timezone

from app import db


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)

    campus = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)

    item_type = db.Column(
        db.String(20),
        nullable=False,
        default="lost"
    )

    item_date = db.Column(db.Date, nullable=False)

    image_url = db.Column(db.String(500), nullable=True)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="active"
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User", backref="items")

