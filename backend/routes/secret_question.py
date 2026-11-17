from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request, g
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models.item import Item
from models.item_secret import ItemSecret, SecretVerification
from utils.auth_middleware import token_required


secret_question_bp = Blueprint("secret_question", __name__)

MAX_FAILED_ATTEMPTS = 3
LOCK_DURATION = timedelta(hours=24)


def utcnow():
    """Naive UTC time, matching how the other models store DateTime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def normalize_answer(answer):
    """Ignore case, extra spaces and surrounding whitespace."""
    return " ".join(answer.lower().split())


def has_verified_secret(item_id, user_id):
    """Return True if the user has correctly answered the item's question."""
    record = SecretVerification.query.filter_by(
        item_id=item_id,
        user_id=user_id
    ).first()

    return bool(record and record.verified_at)


@secret_question_bp.route(
    "/items/<int:item_id>/secret-question",
    methods=["PUT"]
)
@token_required
def set_secret_question(item_id):
    """Let the finder set (or replace) a secret question for a found item."""

    item = Item.query.filter_by(
        id=item_id,
        user_id=g.current_user.id
    ).first()

    if not item:
        return jsonify({"message": "Item not found"}), 404

    if item.item_type != "found":
        return jsonify({
            "message": "Secret questions can only be set for found items"
        }), 400

    data = request.get_json(silent=True) or {}
    question = data.get("question")
    answer = data.get("answer")

    if not isinstance(question, str) or not question.strip():
        return jsonify({"message": "Secret question is required"}), 400

    if not isinstance(answer, str) or not normalize_answer(answer):
        return jsonify({"message": "Secret answer is required"}), 400

    question = question.strip()

    if len(question) > 255:
        return jsonify({
            "message": "Secret question cannot exceed 255 characters"
        }), 400

    if len(answer) > 255:
        return jsonify({
            "message": "Secret answer cannot exceed 255 characters"
        }), 400

    secret = ItemSecret.query.filter_by(item_id=item.id).first()
    answer_hash = generate_password_hash(normalize_answer(answer))

    if secret:
        secret.question = question
        secret.answer_hash = answer_hash
        # A new answer invalidates earlier verifications.
        SecretVerification.query.filter_by(item_id=item.id).delete()
    else:
        db.session.add(ItemSecret(
            item_id=item.id,
            question=question,
            answer_hash=answer_hash
        ))

    db.session.commit()

    return jsonify({
        "message": "Secret question saved successfully",
        "item_id": item.id,
        "question": question
    }), 200


@secret_question_bp.route(
    "/items/<int:item_id>/secret-question",
    methods=["GET"]
)
@token_required
def get_secret_question(item_id):
    """Show the question (never the answer) to someone claiming the item."""

    item = db.session.get(Item, item_id)

    if not item or item.item_type != "found" or item.status != "active":
        return jsonify({"message": "Item not found"}), 404

    secret = ItemSecret.query.filter_by(item_id=item.id).first()

    if not secret:
        return jsonify({
            "item_id": item.id,
            "has_secret_question": False,
            "question": None
        }), 200

    return jsonify({
        "item_id": item.id,
        "has_secret_question": True,
        "question": secret.question,
        "verified": has_verified_secret(item.id, g.current_user.id)
    }), 200


@secret_question_bp.route(
    "/items/<int:item_id>/secret-question/verify",
    methods=["POST"]
)
@token_required
def verify_secret_answer(item_id):
    """Check a claimant's answer. Three wrong answers lock them out for 24h."""

    item = db.session.get(Item, item_id)

    if not item or item.item_type != "found" or item.status != "active":
        return jsonify({"message": "Item not found"}), 404

    if item.user_id == g.current_user.id:
        return jsonify({
            "message": "You cannot verify your own item"
        }), 403

    secret = ItemSecret.query.filter_by(item_id=item.id).first()

    if not secret:
        return jsonify({
            "message": "This item has no secret question"
        }), 404

    data = request.get_json(silent=True) or {}
    answer = data.get("answer")

    if not isinstance(answer, str) or not normalize_answer(answer):
        return jsonify({"message": "Answer is required"}), 400

    record = SecretVerification.query.filter_by(
        item_id=item.id,
        user_id=g.current_user.id
    ).first()

    if not record:
        record = SecretVerification(
            item_id=item.id,
            user_id=g.current_user.id,
            failed_attempts=0
        )
        db.session.add(record)

    if record.verified_at:
        return jsonify({
            "message": "Secret question already verified",
            "verified": True
        }), 200

    now = utcnow()

    if record.locked_until and record.locked_until > now:
        return jsonify({
            "message": "Too many incorrect answers. Try again later.",
            "locked_until": record.locked_until.isoformat()
        }), 429

    if check_password_hash(secret.answer_hash, normalize_answer(answer)):
        record.verified_at = now
        record.failed_attempts = 0
        record.locked_until = None
        db.session.commit()

        return jsonify({
            "message": "Secret question verified successfully",
            "verified": True
        }), 200

    # Restart the counter once an earlier lock has expired.
    if record.locked_until and record.locked_until <= now:
        record.failed_attempts = 0
        record.locked_until = None

    record.failed_attempts += 1

    if record.failed_attempts >= MAX_FAILED_ATTEMPTS:
        record.locked_until = now + LOCK_DURATION

    db.session.commit()

    remaining = max(0, MAX_FAILED_ATTEMPTS - record.failed_attempts)

    return jsonify({
        "message": "Incorrect answer",
        "verified": False,
        "attempts_remaining": remaining
    }), 400
