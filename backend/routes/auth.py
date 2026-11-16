
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models.user import User
from app import db

auth_bp = Blueprint("auth", __name__)


# Student registration API
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    # Check required fields
    if not data or not all(
        data.get(field) for field in ["name", "email", "password"]
    ):
        return jsonify({"message": "All fields are required"}), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    # Validate empty values
    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    # Check duplicate email
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"message": "Email already registered"}), 409

    # Hash password before storing
    hashed_password = generate_password_hash(password)

    # Create new student account
    new_user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful"
    }), 201

