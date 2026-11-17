
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from models.user import User
from app import db
import re

auth_bp = Blueprint("auth", __name__)


# Validate email format
def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))


# Validate password strength
def is_strong_password(password):
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r"[^A-Za-z0-9]", password)
    )


# Student registration API
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True)

    # Check required fields
    if not data or not all(
        data.get(field) for field in ["name", "email", "password"]
    ):
        return jsonify({"message": "All fields are required"}), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    if not name or not email or not password.strip():
        return jsonify({"message": "All fields are required"}), 400

    # Validate email format
    if not is_valid_email(email):
        return jsonify({"message": "Invalid email address"}), 400

    # Validate password strength
    if not is_strong_password(password):
        return jsonify({
            "message": "Password must contain at least 8 characters, "
                       "uppercase, lowercase, number and special character"
        }), 400

    # Check duplicate email
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"message": "Email already registered"}), 409

    # Hash password before storing
    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password)
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already registered"}), 409

    return jsonify({
        "message": "Registration successful"
    }), 201
