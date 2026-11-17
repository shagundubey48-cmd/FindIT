
from flask import Blueprint, request, jsonify, g, current_app
from datetime import date

from sqlalchemy import or_

from app import db
from models.item import Item
from utils.auth_middleware import token_required
from services.cloudinary_service import upload_item_image


items_bp = Blueprint("items", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


# Validate and prepare item report data
def validate_item_data(data):
    required_fields = [
        "title", "description", "category",
        "campus", "location", "item_date"
    ]

    if not data:
        return None, "Request data is required"

    if not all(data.get(field) for field in required_fields):
        return None, "All fields are required"

    text_fields = [
        "title", "description", "category",
        "campus", "location"
    ]

    for field in text_fields:
        if not isinstance(data[field], str) or not data[field].strip():
            return None, "Fields cannot be empty"

    try:
        item_date = date.fromisoformat(data["item_date"])
    except (ValueError, TypeError):
        return None, "Invalid date format. Use YYYY-MM-DD"

    return item_date, None


# Format item details for API responses
def serialize_item(item):
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
        "created_at": (
            item.created_at.isoformat() if item.created_at else None
        )
    }


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
        "item": serialize_item(item)
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


# Upload an image for an item owned by the logged-in user
@items_bp.route("/items/<int:item_id>/image", methods=["POST"])
@token_required
def upload_image(item_id):
    item = Item.query.filter_by(
        id=item_id,
        user_id=g.current_user.id
    ).first()

    if not item:
        return jsonify({"message": "Item not found"}), 404

    if "image" not in request.files:
        return jsonify({"message": "Image file is required"}), 400

    image_file = request.files["image"]

    if not image_file.filename:
        return jsonify({"message": "No image selected"}), 400

    if "." not in image_file.filename:
        return jsonify({
            "message": "Only JPG, JPEG, PNG and WEBP images are allowed"
        }), 400

    extension = image_file.filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return jsonify({
            "message": "Only JPG, JPEG, PNG and WEBP images are allowed"
        }), 400

    try:
        image_url = upload_item_image(image_file)
    except Exception:
        current_app.logger.exception("Cloudinary image upload failed")
        return jsonify({"message": "Image upload failed"}), 502

    item.image_url = image_url
    db.session.commit()

    return jsonify({
        "message": "Image uploaded successfully",
        "image_url": item.image_url,
        "item_id": item.id
    }), 200


# View and search active lost and found items
@items_bp.route("/items", methods=["GET"])
@token_required
def get_items():
    query = Item.query.filter_by(status="active")

    # Filter by lost or found type
    item_type = request.args.get("type", "").strip().lower()

    if item_type:
        if item_type not in ["lost", "found"]:
            return jsonify({
                "message": "Type must be either lost or found"
            }), 400

        query = query.filter_by(item_type=item_type)

    # Search in item title and description
    keyword = request.args.get("q", "").strip()

    if keyword:
        search_term = f"%{keyword}%"
        query = query.filter(
            or_(
                Item.title.ilike(search_term),
                Item.description.ilike(search_term)
            )
        )

    # Filter by category
    category = request.args.get("category", "").strip()

    if category:
        query = query.filter(Item.category.ilike(category))

    # Filter by campus
    campus = request.args.get("campus", "").strip()

    if campus:
        query = query.filter(Item.campus.ilike(campus))

    items = query.order_by(
        Item.created_at.desc(),
        Item.id.desc()
    ).all()

    return jsonify({
        "count": len(items),
        "items": [serialize_item(item) for item in items]
    }), 200


# View details of one active item
@items_bp.route("/items/<int:item_id>", methods=["GET"])
@token_required
def get_item_details(item_id):
    item = Item.query.filter_by(
        id=item_id,
        status="active"
    ).first()

    if not item:
        return jsonify({"message": "Item not found"}), 404

    return jsonify({
        "item": serialize_item(item)
    }), 200
