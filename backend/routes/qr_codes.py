from io import BytesIO

import qrcode
from flask import Blueprint, jsonify, request, g, send_file, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app import db
from models.item import Item
from models.claim import Claim
from models.handover import Handover
from utils.auth_middleware import token_required


qr_codes_bp = Blueprint("qr_codes", __name__)

HANDOVER_QR_MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # 7 days


def make_qr_png(content):
    """Render text as a PNG QR code and return it as an in-memory file."""
    image = qrcode.make(content)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def handover_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="findit-handover-qr"
    )


@qr_codes_bp.route("/items/<int:item_id>/qr", methods=["GET"])
@token_required
def get_item_qr(item_id):
    """Return a QR code that links to the item's page.

    The reporter can print it and attach it to the physical item or a
    notice board; an administrator can also generate it.
    """

    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({"message": "Item not found"}), 404

    if not (g.current_user.is_admin or item.user_id == g.current_user.id):
        return jsonify({"message": "Access denied"}), 403

    item_url = f"{current_app.config['FRONTEND_URL']}/items/{item.id}"

    return send_file(
        make_qr_png(item_url),
        mimetype="image/png",
        download_name=f"findit-item-{item.id}.png"
    )


@qr_codes_bp.route("/claims/<int:claim_id>/handover-qr", methods=["GET"])
@token_required
def get_handover_qr(claim_id):
    """Give an approved claimant a QR code to show at the collection desk."""

    claim = Claim.query.filter_by(
        id=claim_id,
        claimant_id=g.current_user.id
    ).first()

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    if claim.status != "approved":
        return jsonify({
            "message": "A handover QR code is only available for approved claims"
        }), 400

    if Handover.query.filter_by(claim_id=claim.id).first():
        return jsonify({
            "message": "This item has already been handed over"
        }), 409

    token = handover_serializer().dumps({"claim_id": claim.id})

    return send_file(
        make_qr_png(token),
        mimetype="image/png",
        download_name=f"findit-handover-{claim.id}.png"
    )


@qr_codes_bp.route("/admin/handover-qr/verify", methods=["POST"])
@token_required
def verify_handover_qr():
    """Let an administrator scan a claimant's QR code before handing over."""

    if not g.current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}
    token = data.get("token")

    if not isinstance(token, str) or not token.strip():
        return jsonify({"message": "QR token is required"}), 400

    try:
        payload = handover_serializer().loads(
            token.strip(),
            max_age=HANDOVER_QR_MAX_AGE_SECONDS
        )
    except SignatureExpired:
        return jsonify({"message": "QR code has expired"}), 400
    except BadSignature:
        return jsonify({"message": "Invalid QR code"}), 400

    claim = db.session.get(Claim, payload.get("claim_id"))

    if not claim or claim.status != "approved":
        return jsonify({"message": "Claim is not approved"}), 400

    if Handover.query.filter_by(claim_id=claim.id).first():
        return jsonify({
            "message": "Handover has already been recorded"
        }), 409

    return jsonify({
        "valid": True,
        "claim_id": claim.id,
        "item_id": claim.item_id,
        "item_title": claim.item.title,
        "claimant_name": claim.claimant.name,
        "claimant_email": claim.claimant.email
    }), 200
