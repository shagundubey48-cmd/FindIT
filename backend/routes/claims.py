from flask import Blueprint, jsonify, request, g

from app import db
from models.item import Item
from models.claim import Claim
from models.item_secret import ItemSecret
from routes.secret_question import has_verified_secret
from utils.auth_middleware import token_required


claims_bp = Blueprint("claims", __name__)

ALLOWED_PROOF_TYPES = {
    "identifying_mark",
    "serial_number",
    "purchase_proof",
    "other"
}


def serialize_claim(claim):
    """Convert claim and tracking information into JSON."""
    return {
        "id": claim.id,
        "item_id": claim.item_id,
        "item_title": claim.item.title,
        "item_image": claim.item.image_url,
        "ownership_details": claim.ownership_details,
        "proof_type": claim.proof_type,
        "proof_details": claim.proof_details,
        "status": claim.status,
        "admin_remarks": claim.admin_remarks,
        "status_updated_at": claim.status_updated_at.isoformat(),
        "created_at": claim.created_at.isoformat(),
        "updated_at": claim.updated_at.isoformat()
    }


@claims_bp.route(
    "/items/<int:item_id>/claims",
    methods=["POST"]
)
@token_required
def submit_claim(item_id):
    """Submit an ownership claim for a found item."""

    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({"message": "Item not found"}), 404

    if item.item_type != "found":
        return jsonify({
            "message": "Claims can only be submitted for found items"
        }), 400

    if item.status != "active":
        return jsonify({
            "message": "This item is no longer available for claiming"
        }), 400

    if item.user_id == g.current_user.id:
        return jsonify({
            "message": "You cannot claim an item reported by yourself"
        }), 403

    # US-16: the finder's secret question must be answered first.
    if (
        ItemSecret.query.filter_by(item_id=item_id).first()
        and not has_verified_secret(item_id, g.current_user.id)
    ):
        return jsonify({
            "message": "Answer the item's secret question before claiming"
        }), 403

    data = request.get_json(silent=True) or {}
    ownership_details = data.get("ownership_details", "")

    if not isinstance(ownership_details, str):
        return jsonify({
            "message": "Ownership details must be text"
        }), 400

    ownership_details = ownership_details.strip()

    if not ownership_details:
        return jsonify({
            "message": "Ownership details are required"
        }), 400

    if len(ownership_details) > 2000:
        return jsonify({
            "message": "Ownership details cannot exceed 2000 characters"
        }), 400

    existing_claim = Claim.query.filter_by(
        claimant_id=g.current_user.id,
        item_id=item_id,
        status="pending"
    ).first()

    if existing_claim:
        return jsonify({
            "message": "You already have a pending claim for this item"
        }), 409

    claim = Claim(
        claimant_id=g.current_user.id,
        item_id=item_id,
        ownership_details=ownership_details,
        status="pending"
    )

    db.session.add(claim)
    db.session.commit()

    return jsonify({
        "message": "Ownership claim submitted successfully",
        "claim": serialize_claim(claim)
    }), 201


@claims_bp.route("/claims", methods=["GET"])
@token_required
def get_my_claims():
    """View all claims submitted by the logged-in user."""

    claims = Claim.query.filter_by(
        claimant_id=g.current_user.id
    ).order_by(
        Claim.created_at.desc()
    ).all()

    return jsonify({
        "count": len(claims),
        "claims": [
            serialize_claim(claim)
            for claim in claims
        ]
    }), 200


@claims_bp.route(
    "/claims/<int:claim_id>/evidence",
    methods=["PUT"]
)
@token_required
def submit_claim_evidence(claim_id):
    """Submit or update additional ownership verification evidence."""

    claim = Claim.query.filter_by(
        id=claim_id,
        claimant_id=g.current_user.id
    ).first()

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    if claim.status != "pending":
        return jsonify({
            "message": "Evidence can only be updated for pending claims"
        }), 400

    data = request.get_json(silent=True) or {}

    proof_type = data.get("proof_type")
    proof_details = data.get("proof_details")

    if not isinstance(proof_type, str) or proof_type not in ALLOWED_PROOF_TYPES:
        return jsonify({
            "message": "Select a valid proof type"
        }), 400

    if not isinstance(proof_details, str):
        return jsonify({
            "message": "Proof details must be text"
        }), 400

    proof_details = proof_details.strip()

    if not proof_details:
        return jsonify({
            "message": "Proof details are required"
        }), 400

    if len(proof_details) > 2000:
        return jsonify({
            "message": "Proof details cannot exceed 2000 characters"
        }), 400

    claim.proof_type = proof_type
    claim.proof_details = proof_details

    db.session.commit()

    return jsonify({
        "message": "Ownership evidence submitted successfully",
        "claim": serialize_claim(claim)
    }), 200


@claims_bp.route(
    "/claims/<int:claim_id>",
    methods=["GET"]
)
@token_required
def get_claim_details(claim_id):
    """View one claim and its evidence."""

    claim = Claim.query.filter_by(
        id=claim_id,
        claimant_id=g.current_user.id
    ).first()

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    return jsonify({
        "claim": serialize_claim(claim)
    }), 200


@claims_bp.route(
    "/claims/<int:claim_id>/status",
    methods=["GET"]
)
@token_required
def track_claim_status(claim_id):
    """Track the status and administrator remarks of a claim."""

    claim = Claim.query.filter_by(
        id=claim_id,
        claimant_id=g.current_user.id
    ).first()

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    return jsonify({
        "claim_id": claim.id,
        "item_id": claim.item_id,
        "item_title": claim.item.title,
        "status": claim.status,
        "admin_remarks": claim.admin_remarks,
        "status_updated_at": claim.status_updated_at.isoformat()
    }), 200
