from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request, g

from app import db
from models.item import Item
from models.claim import Claim
from utils.auth_middleware import token_required


unclaimed_bp = Blueprint("unclaimed", __name__)

DEFAULT_UNCLAIMED_DAYS = 30

# Action requested by the admin -> status stored on the item.
ACTION_STATUSES = {
    "archive": "archived",
    "donate": "donated",
    "dispose": "disposed"
}


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def has_pending_claim(item_id):
    return Claim.query.filter_by(
        item_id=item_id,
        status="pending"
    ).first() is not None


def serialize_unclaimed_item(item):
    created_at = item.created_at
    age_days = (utcnow() - created_at).days if created_at else None

    claims = Claim.query.filter_by(item_id=item.id).all()

    return {
        "id": item.id,
        "title": item.title,
        "category": item.category,
        "campus": item.campus,
        "location": item.location,
        "item_date": item.item_date.isoformat(),
        "image_url": item.image_url,
        "reported_by": item.user.name,
        "age_days": age_days,
        "total_claims": len(claims),
        "rejected_claims": sum(1 for c in claims if c.status == "rejected"),
        "created_at": created_at.isoformat() if created_at else None
    }


@unclaimed_bp.route("/admin/unclaimed-items", methods=["GET"])
@token_required
def list_unclaimed_items():
    """List found items nobody has successfully claimed after N days."""

    if not g.current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403

    days_arg = request.args.get("days", str(DEFAULT_UNCLAIMED_DAYS))

    try:
        days = int(days_arg)
    except ValueError:
        return jsonify({"message": "days must be a whole number"}), 400

    if days < 1:
        return jsonify({"message": "days must be at least 1"}), 400

    cutoff = utcnow() - timedelta(days=days)

    candidates = Item.query.filter(
        Item.item_type == "found",
        Item.status == "active",
        Item.created_at <= cutoff
    ).order_by(Item.created_at.asc()).all()

    # Items with a claim under review are not "unclaimed" yet.
    items = [item for item in candidates if not has_pending_claim(item.id)]

    return jsonify({
        "older_than_days": days,
        "count": len(items),
        "items": [serialize_unclaimed_item(item) for item in items]
    }), 200


@unclaimed_bp.route(
    "/admin/unclaimed-items/<int:item_id>/action",
    methods=["POST"]
)
@token_required
def handle_unclaimed_item(item_id):
    """Archive, donate or dispose of an unclaimed found item."""

    if not g.current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403

    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({"message": "Item not found"}), 404

    if item.item_type != "found" or item.status != "active":
        return jsonify({
            "message": "Only active found items can be processed"
        }), 409

    if has_pending_claim(item.id):
        return jsonify({
            "message": "This item has a pending claim and cannot be processed"
        }), 409

    data = request.get_json(silent=True) or {}
    action = data.get("action")
    remarks = data.get("admin_remarks")

    if action not in ACTION_STATUSES:
        return jsonify({
            "message": "Action must be archive, donate, or dispose"
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

    item.status = ACTION_STATUSES[action]
    item.admin_remarks = remarks
    item.moderated_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        "message": f"Item {item.status} successfully",
        "item": {
            "id": item.id,
            "title": item.title,
            "status": item.status,
            "admin_remarks": item.admin_remarks,
            "moderated_at": item.moderated_at.isoformat()
        }
    }), 200
