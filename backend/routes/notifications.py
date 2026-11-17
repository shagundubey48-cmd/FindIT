
from flask import Blueprint, jsonify, g

from models.notification import Notification
from utils.auth_middleware import token_required
from app import db


notifications_bp = Blueprint("notifications", __name__)


def serialize_notification(notification):
    return {
        "id": notification.id,
        "message": notification.message,
        "item_id": notification.item_id,
        "matched_item_id": notification.matched_item_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat()
    }


@notifications_bp.route("/notifications", methods=["GET"])
@token_required
def get_notifications():
    """Return notifications belonging to the logged-in user."""

    notifications = Notification.query.filter_by(
        user_id=g.current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    unread_count = sum(
        1 for notification in notifications
        if not notification.is_read
    )

    return jsonify({
        "count": len(notifications),
        "unread_count": unread_count,
        "notifications": [
            serialize_notification(notification)
            for notification in notifications
        ]
    }), 200


@notifications_bp.route(
    "/notifications/<int:notification_id>/read",
    methods=["PATCH"]
)
@token_required
def mark_notification_read(notification_id):
    """Mark one of the user's notifications as read."""

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=g.current_user.id
    ).first()

    if not notification:
        return jsonify({
            "message": "Notification not found"
        }), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({
        "message": "Notification marked as read",
        "notification": serialize_notification(notification)
    }), 200

