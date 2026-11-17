
from flask import Blueprint, request, jsonify, g
from datetime import date

from app import db
from models.item import Item
from utils.auth_middleware import token_required


items_bp = Blueprint("items", __name__)


# Validate and prepare item report data
def validate_item_data(data):
    required_fields = [
        "title",
        "description",
        "category",
        "campus",
        "location",
        "item_date"
    ]

    if not data:
        return None, "Request data is required"

    if not all(data.get(field) for field in required_fields):
        return None, "All fields are required"

    text_fields = [
        "title",
        "description",
        "category",
        "campus",
        "location"
    ]

    for field in text_fields:
        if not isinstance(data[field], str) or not data[field].strip():
            return None, "Fields cannot be empty"

    try:
        item_date = date.fromisoformat(data["item_date"])
    except (ValueError, TypeError):
        return None, "Invalid date format. Use YYYY-MM-DD"

    return item_date, None


# Create a lost or found item report
def create_item_report(item_type):
    data = request.get_json(silent=True)
    item_date, error = validate_item_data(data)

    if error:
        return jsonify({"message": error}), 400

    item = Item(
        user_id=g.current_user.id,
        title=data["title"].strip(),
        description=data["description"].strip(),
        category=data["category"].strip(),
        campus=data["campus"].strip(),
        location=data["location"].strip(),
        item_type=item_type,
        item_date=item_date,
        status="active"
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": f"{item_type.capitalize()} item reported successfully",
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


# Report a lost item
@items_bp.route("/items/lost", methods=["POST"])
@token_required
def report_lost_item():
    return create_item_report("lost")


# Report a found item
@items_bp.route("/items/found", methods=["POST"])
@token_required
def report_found_item():
    return create_item_report("found")
