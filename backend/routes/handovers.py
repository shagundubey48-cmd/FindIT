
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, g
from sqlalchemy import or_

from app import db
from models.handover import Handover
from models.claim import Claim
from models.item import Item
from utils.auth_middleware import token_required


handovers_bp = Blueprint("handovers", __name__)


def serialize_handover(handover):
    """Convert a handover record into JSON."""
    return {
        "id": handover.id,
        "claim_id": handover.claim_id,
        "item_id": handover.item_id,
        "item_title": handover.item.title,
        "item_type": handover.item.item_type,
        "handed_over_by": handover.handed_over_by,
        "administrator_name": handover.administrator.name,
        "received_by": handover.received_by,
        "recipient_name": handover.recipient.name,
        "handover_notes": handover.handover_notes,
        "handed_over_at": handover.handed_over_at.isoformat()
    }


@handovers_bp.route(
    "/admin/claims/<int:claim_id>/handover",
    methods=["POST"]
)
@token_required
def confirm_handover(claim_id):
    """Allow an administrator to record a completed item handover."""

    if not g.current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403

    claim = db.session.get(Claim, claim_id)

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    if claim.status != "approved":
        return jsonify({
            "message": "Only approved claims can be handed over"
        }), 400

    existing = Handover.query.filter_by(claim_id=claim.id).first()

    if existing:
        return jsonify({
            "message": "Handover has already been recorded"
        }), 409

    item = db.session.get(Item, claim.item_id)

    if not item or item.status != "claimed":
        return jsonify({
            "message": "Item is not available for handover"
        }), 409

    data = request.get_json(silent=True) or {}
    notes = data.get("handover_notes")

    if notes is not None and not isinstance(notes, str):
        return jsonify({
            "message": "Handover notes must be text"
        }), 400

    if isinstance(notes, str):
        notes = notes.strip()

    if notes and len(notes) > 2000:
        return jsonify({
            "message": "Handover notes cannot exceed 2000 characters"
        }), 400

    handover = Handover(
        claim_id=claim.id,
        item_id=item.id,
        handed_over_by=g.current_user.id,
        received_by=claim.claimant_id,
        handover_notes=notes or None,
        handed_over_at=datetime.now(timezone.utc)
    )

    db.session.add(handover)
    db.session.commit()

    return jsonify({
        "message": "Item handover recorded successfully",
        "handover": serialize_handover(handover)
    }), 201


@handovers_bp.route(
    "/items/<int:item_id>/handover-history",
    methods=["GET"]
)
@token_required
def get_item_handover_history(item_id):
    """Allow the reporter, recipient, or admin to view item handovers."""

    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({"message": "Item not found"}), 404

    handovers = Handover.query.filter_by(
        item_id=item_id
    ).order_by(Handover.handed_over_at.desc()).all()

    is_reporter = item.user_id == g.current_user.id
    is_recipient = any(
        handover.received_by == g.current_user.id
        for handover in handovers
    )

    if not (g.current_user.is_admin or is_reporter or is_recipient):
        return jsonify({"message": "Access denied"}), 403

    return jsonify({
        "item_id": item.id,
        "item_title": item.title,
        "count": len(handovers),
        "history": [
            serialize_handover(handover)
            for handover in handovers
        ]
    }), 200


@handovers_bp.route("/handovers/my", methods=["GET"])
@token_required
def get_my_handovers():
    """Show handovers where the user is the recipient or item reporter."""

    handovers = Handover.query.join(
        Item,
        Handover.item_id == Item.id
    ).filter(
        or_(
            Handover.received_by == g.current_user.id,
            Item.user_id == g.current_user.id
        )
    ).order_by(
        Handover.handed_over_at.desc()
    ).all()

    return jsonify({
        "count": len(handovers),
        "handovers": [
            serialize_handover(handover)
            for handover in handovers
        ]
    }), 200
