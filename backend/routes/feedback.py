
from flask import Blueprint, jsonify, request, g

from app import db
from models.feedback import Feedback
from models.handover import Handover
from utils.auth_middleware import token_required


feedback_bp = Blueprint("feedback", __name__)


def serialize_feedback(feedback):
    """Convert feedback into a JSON response."""
    return {
        "id": feedback.id,
        "handover_id": feedback.handover_id,
        "user_id": feedback.user_id,
        "user_name": feedback.user.name,
        "item_id": feedback.handover.item_id,
        "item_title": feedback.handover.item.title,
        "rating": feedback.rating,
        "comment": feedback.comment,
        "created_at": feedback.created_at.isoformat()
    }


@feedback_bp.route(
    "/handovers/<int:handover_id>/feedback",
    methods=["POST"]
)
@token_required
def submit_feedback(handover_id):
    """Allow the recipient to rate a completed handover."""

    handover = db.session.get(Handover, handover_id)

    if not handover:
        return jsonify({"message": "Handover not found"}), 404

    if handover.received_by != g.current_user.id:
        return jsonify({
            "message": "Only the recipient can submit feedback"
        }), 403

    existing = Feedback.query.filter_by(
        handover_id=handover_id
    ).first()

    if existing:
        return jsonify({
            "message": "Feedback has already been submitted"
        }), 409

    data = request.get_json(silent=True) or {}
    rating = data.get("rating")
    comment = data.get("comment")

    if type(rating) is not int or not 1 <= rating <= 5:
        return jsonify({
            "message": "Rating must be an integer between 1 and 5"
        }), 400

    if comment is not None and not isinstance(comment, str):
        return jsonify({
            "message": "Comment must be text"
        }), 400

    if isinstance(comment, str):
        comment = comment.strip()

    if comment and len(comment) > 1000:
        return jsonify({
            "message": "Comment cannot exceed 1000 characters"
        }), 400

    feedback = Feedback(
        handover_id=handover_id,
        user_id=g.current_user.id,
        rating=rating,
        comment=comment or None
    )

    db.session.add(feedback)
    db.session.commit()

    return jsonify({
        "message": "Feedback submitted successfully",
        "feedback": serialize_feedback(feedback)
    }), 201


@feedback_bp.route("/feedback/my", methods=["GET"])
@token_required
def get_my_feedback():
    """Return feedback submitted by the logged-in user."""

    feedback_list = Feedback.query.filter_by(
        user_id=g.current_user.id
    ).order_by(
        Feedback.created_at.desc()
    ).all()

    return jsonify({
        "count": len(feedback_list),
        "feedback": [
            serialize_feedback(feedback)
            for feedback in feedback_list
        ]
    }), 200


@feedback_bp.route("/admin/feedback", methods=["GET"])
@token_required
def get_all_feedback():
    """Allow administrators to view all submitted feedback."""

    if not g.current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403

    feedback_list = Feedback.query.order_by(
        Feedback.created_at.desc()
    ).all()

    return jsonify({
        "count": len(feedback_list),
        "feedback": [
            serialize_feedback(feedback)
            for feedback in feedback_list
        ]
    }), 200

