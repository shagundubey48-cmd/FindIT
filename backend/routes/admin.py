
from flask import Blueprint, jsonify, g

from app import db
from models.user import User
from models.item import Item
from models.claim import Claim
from utils.auth_middleware import token_required


admin_bp = Blueprint("admin", __name__)


def check_admin():
    """Check whether the logged-in user has administrator access."""
    if not g.current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403
    return None


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
            {
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
                "created_at": item.created_at.isoformat()
            }
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
            {
                "id": claim.id,
                "claimant_id": claim.claimant_id,
                "claimant_name": claim.claimant.name,
                "item_id": claim.item_id,
                "item_title": claim.item.title,
                "ownership_details": claim.ownership_details,
                "proof_type": claim.proof_type,
                "proof_details": claim.proof_details,
                "status": claim.status,
                "admin_remarks": claim.admin_remarks,
                "created_at": claim.created_at.isoformat()
            }
            for claim in claims
        ]
    }), 200

