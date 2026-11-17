
from flask import Blueprint, request, jsonify, g
from datetime import date

from app import db
from models.item import Item
from utils.auth_middleware import token_required


items_bp = Blueprint("items", __name__)


# Create a new lost-item report
@items_bp.route("/items/lost", methods=["POST"])
@token_required
def report_lost_item():
    data = request.get_json(silent=True)

    required_fields = [
        "title",
        "description",
        "category",
        "campus",
        "location",
        "item_date"
    ]

    if not data:
        return jsonify({"message": "Request data is required"}), 400

    if not all(data.get(field) for field in required_fields):
        return jsonify({"message": "All fields are required"}), 400

    # Validate item date
    try:
        item_date = date.fromisoformat(data["item_date"])
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Create lost-item record
    item = Item(
        user_id=g.current_user.id,
        title=data["title"].strip(),
        description=data["description"].strip(),
        category=data["category"].strip(),
        campus=data["campus"].strip(),
        location=data["location"].strip(),
        item_type="lost",
        item_date=item_date,
        status="active"
    )

    # Reject empty text fields
    if not all([
        item.title,
        item.description,
        item.category,
        item.campus,
        item.location
    ]):
        return jsonify({"message": "Fields cannot be empty"}), 400

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "Lost item reported successfully",
        "item": {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "category": item.category,
            "campus": item.campus,
            "location": item.location,
            "item_type": item.item_type,
            "item_date": item.item_date.isoformat(),
            "status": item.status
        }
    }), 201

