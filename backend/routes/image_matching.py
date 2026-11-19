from flask import Blueprint, jsonify
from app import db
from models.item import Item
from utils.auth_middleware import token_required
from services.image_matching_service import calculate_image_similarity


image_matching_bp = Blueprint("image_matching", __name__)


@image_matching_bp.route(
    "/items/<int:item_id>/image-matches",
    methods=["GET"]
)
@token_required
def get_image_matches(item_id):
    """Find visually similar images from opposite-type item reports."""

    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({"message": "Item not found"}), 404

    if not item.image_url:
        return jsonify({
            "message": "This item does not have an uploaded image",
            "matches": [],
            "count": 0
        }), 200

    opposite_type = "found" if item.item_type == "lost" else "lost"

    candidates = Item.query.filter(
        Item.item_type == opposite_type,
        Item.status == "active",
        Item.id != item.id,
        Item.user_id != item.user_id,
        Item.image_url.isnot(None)
    ).all()

    matches = []

    for candidate in candidates:
        try:
            score = calculate_image_similarity(
                item.image_url,
                candidate.image_url
            )

            # Only return candidates with at least 70% visual similarity.
            if score >= 70:
                matches.append({
                    "id": candidate.id,
                    "title": candidate.title,
                    "description": candidate.description,
                    "category": candidate.category,
                    "campus": candidate.campus,
                    "location": candidate.location,
                    "item_type": candidate.item_type,
                    "item_date": candidate.item_date.isoformat(),
                    "image_url": candidate.image_url,
                    "similarity_score": score
                })

        except Exception:
            # Skip an image if it cannot be downloaded or processed.
            continue

    matches.sort(
        key=lambda match: match["similarity_score"],
        reverse=True
    )

    return jsonify({
        "item_id": item.id,
        "count": len(matches),
        "matches": matches
    }), 200
