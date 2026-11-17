
from flask import Blueprint, jsonify
from models.item import Item
from utils.auth_middleware import token_required
from services.matching_service import calculate_match_score
from services.image_matching_service import calculate_image_similarity


combined_matching_bp = Blueprint("combined_matching", __name__)


@combined_matching_bp.route(
    "/items/<int:item_id>/matched-items",
    methods=["GET"]
)
@token_required
def get_matched_items(item_id):
    """Return text and image matches together in ranked order."""

    item = Item.query.get(item_id)

    if not item:
        return jsonify({"message": "Item not found"}), 404

    opposite_type = "found" if item.item_type == "lost" else "lost"

    candidates = Item.query.filter(
        Item.item_type == opposite_type,
        Item.status == "active",
        Item.id != item.id,
        Item.user_id != item.user_id
    ).all()

    matches = []

    for candidate in candidates:
        text_score = calculate_match_score(item, candidate)

        image_score = None

        if item.image_url and candidate.image_url:
            try:
                image_score = calculate_image_similarity(
                    item.image_url,
                    candidate.image_url
                )
            except Exception:
                # Continue with text matching if image comparison fails.
                image_score = None

        # Keep a candidate if either matching method finds a match.
        if text_score < 20 and (
            image_score is None or image_score < 70
        ):
            continue

        if image_score is not None:
            combined_score = (
                text_score * 0.60 + image_score * 0.40
            )
        else:
            combined_score = text_score

        if text_score >= 20 and image_score is not None and image_score >= 70:
            match_type = "text_and_image"
        elif image_score is not None and image_score >= 70:
            match_type = "image"
        else:
            match_type = "text"

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
            "text_score": text_score,
            "image_score": image_score,
            "match_score": round(combined_score, 2),
            "match_type": match_type
        })

    matches.sort(
        key=lambda match: match["match_score"],
        reverse=True
    )

    return jsonify({
        "item_id": item.id,
        "count": len(matches),
        "matches": matches
    }), 200

