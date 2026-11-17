
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, g

from app import db
from models.user import User
from models.item import Item
from models.claim import Claim
from utils.auth_middleware import token_required


admin_bp = Blueprint("admin", __name__)

ALLOWED_ITEM_STATUSES = {"active", "resolved", "removed"}


def check_admin():
    """Check whether the logged-in user is an administrator."""
    if not g.current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403
    return None


def serialize_admin_claim(claim):
    """Return complete claim information for administrator review."""
    return {
        "id": claim.id,
        "claimant_id": claim.claimant_id,
        "claimant_name": claim.claimant.name,
        "claimant_email": claim.claimant.email,
        "item_id": claim.item_id,
        "item_title": claim.item.title,
        "item_image": claim.item.image_url,
        "ownership_details": claim.ownership_details,
        "proof_type": claim.proof_type,
        "proof_details": claim.proof_details,
        "status": claim.status,
        "admin_remarks": claim.admin_remarks,
        "status_updated_at": claim.status_updated_at.isoformat(),
        "created_at": claim.created_at.isoformat()
    }


def serialize_admin_item(item):
    """Return item information including moderation details."""
    return {
        "id": item.id,
        "user_id": item.user_id,
        "title": item.title,
        "description": item.description,
        "category": item.category,
        "campus": item.campus,
        "location": item.location,
        "item_type": item.item_type,
        "item_date": item.item_date.isoformat(),
        "image_url": item.image_url,
        "status": item.status,
        "admin_remarks": item.admin_remarks,
        "moderated_at": (
            item.moderated_at.isoformat()
            if item.moderated_at else None
        ),
        "created_at": item.created_at.isoformat()
    }


@admin_bp.route("/admin/dashboard", methods=["GET"])
@token_required
def get_admin_dashboard():
    """Return an overview of platform activity."""

    access_error = check_admin()
    if access_error:
        return access_error

    return jsonify({
        "total_users": User.query.count(),
        "total_items": Item.query.count(),
        "active_lost_items": Item.query.filter_by(
            item_type="lost",
            status="active"
        ).count(),
        "active_found_items": Item.query.filter_by(
            item_type="found",
            status="active"
        ).count(),
        "pending_claims": Claim.query.filter_by(
            status="pending"
        ).count(),
        "total_claims": Claim.query.count()
    }), 200


@admin_bp.route("/admin/items", methods=["GET"])
@token_required
def get_all_admin_items():
    """Allow administrators to view all lost and found reports."""

    access_error = check_admin()
    if access_error:
        return access_error

    items = Item.query.order_by(Item.created_at.desc()).all()

    return jsonify({
        "count": len(items),
        "items": [
            serialize_admin_item(item)
            for item in items
        ]
    }), 200


@admin_bp.route("/admin/claims", methods=["GET"])
@token_required
def get_all_admin_claims():
    """Allow administrators to view all submitted ownership claims."""

    access_error = check_admin()
    if access_error:
        return access_error

    claims = Claim.query.order_by(Claim.created_at.desc()).all()

    return jsonify({
        "count": len(claims),
        "claims": [
            serialize_admin_claim(claim)
            for claim in claims
        ]
    }), 200


@admin_bp.route(
    "/admin/claims/<int:claim_id>",
    methods=["GET"]
)
@token_required
def get_admin_claim_details(claim_id):
    """View full details and evidence for one ownership claim."""

    access_error = check_admin()
    if access_error:
        return access_error

    claim = db.session.get(Claim, claim_id)

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    return jsonify({
        "claim": serialize_admin_claim(claim)
    }), 200


@admin_bp.route(
    "/admin/claims/<int:claim_id>/decision",
    methods=["PATCH"]
)
@token_required
def decide_claim(claim_id):
    """Approve or reject a pending ownership claim."""

    access_error = check_admin()
    if access_error:
        return access_error

    claim = db.session.get(Claim, claim_id)

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    if claim.status != "pending":
        return jsonify({
            "message": "Only pending claims can be reviewed"
        }), 400

    data = request.get_json(silent=True) or {}

    decision = data.get("status")
    remarks = data.get("admin_remarks")

    if decision not in {"approved", "rejected"}:
        return jsonify({
            "message": "Status must be approved or rejected"
        }), 400

    if not isinstance(remarks, str) or not remarks.strip():
        return jsonify({
            "message": "Administrator remarks are required"
        }), 400

    remarks = remarks.strip()

    if len(remarks) > 2000:
        return jsonify({
            "message": "Administrator remarks cannot exceed 2000 characters"
        }), 400

    item = db.session.get(Item, claim.item_id)

    if decision == "approved":
        if item.status != "active":
            return jsonify({
                "message": "This item is no longer available for approval"
            }), 409

        item.status = "claimed"

        other_claims = Claim.query.filter(
            Claim.item_id == item.id,
            Claim.id != claim.id,
            Claim.status == "pending"
        ).all()

        now = datetime.now(timezone.utc)

        for other_claim in other_claims:
            other_claim.status = "rejected"
            other_claim.admin_remarks = (
                "Another ownership claim was approved for this item."
            )
            other_claim.status_updated_at = now

    claim.status = decision
    claim.admin_remarks = remarks
    claim.status_updated_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        "message": f"Claim {decision} successfully",
        "claim": serialize_admin_claim(claim)
    }), 200


@admin_bp.route(
    "/admin/items/<int:item_id>/moderation",
    methods=["PATCH"]
)
@token_required
def moderate_item(item_id):
    """Update a report's status and record administrator remarks."""

    access_error = check_admin()
    if access_error:
        return access_error

    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({"message": "Item not found"}), 404

    if item.status == "claimed":
        return jsonify({
            "message": "A claimed item cannot be moderated"
        }), 409

    data = request.get_json(silent=True) or {}

    new_status = data.get("status")
    remarks = data.get("admin_remarks")

    if new_status not in ALLOWED_ITEM_STATUSES:
        return jsonify({
            "message": "Status must be active, resolved, or removed"
        }), 400

    if not isinstance(remarks, str) or not remarks.strip():
        return jsonify({
            "message": "Administrator remarks are required"
        }), 400

    remarks = remarks.strip()

    if len(remarks) > 2000:
        return jsonify({
            "message": "Administrator remarks cannot exceed 2000 characters"
        }), 400

    item.status = new_status
    item.admin_remarks = remarks
    item.moderated_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        "message": "Item report updated successfully",
        "item": serialize_admin_item(item)
    }), 200
