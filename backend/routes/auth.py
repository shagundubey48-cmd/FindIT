from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models.user import User
from app import db
from services.email_service import send_verification_email
from utils.auth_middleware import token_required

from datetime import datetime, timedelta, timezone
import re
import secrets
import hashlib
import jwt


auth_bp = Blueprint("auth", __name__)


# Validate email format
def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))


# Check password strength
def is_strong_password(password):
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r"[^A-Za-z0-9]", password)
    )


# Register a new user
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not data or not all(data.get(field) for field in ["name", "email", "password"]):
        return jsonify({"message": "All fields are required"}), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    if not name or not email or not password.strip():
        return jsonify({"message": "All fields are required"}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email address"}), 400

    allowed_domains = current_app.config["ALLOWED_EMAIL_DOMAINS"]

    if email.rsplit("@", 1)[1] not in allowed_domains:
        return jsonify({"message": "Please use your JIIT college email"}), 400

    if not is_strong_password(password):
        return jsonify({
            "message": "Password must contain at least 8 characters, "
                       "uppercase, lowercase, number and special character"
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    token = secrets.token_urlsafe(32)

    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        is_verified=False,
        verification_token_hash=hashlib.sha256(token.encode()).hexdigest(),
        verification_token_expires_at=(
            datetime.now(timezone.utc).replace(tzinfo=None)
            + timedelta(minutes=15)
        )
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already registered"}), 409

    try:
        send_verification_email(email, token)
    except Exception:
        current_app.logger.exception("Verification email could not be sent")
        return jsonify({
            "message": "Account created, but verification email could not be sent. Please contact support."
        }), 500

    return jsonify({
        "message": "Registration successful. Please verify your email."
    }), 201


# Verify the user's college email
@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    user = User.query.filter_by(
        verification_token_hash=token_hash
    ).first()

    if not user:
        return jsonify({"message": "Invalid verification link"}), 400

    if (
        not user.verification_token_expires_at
        or user.verification_token_expires_at
        < datetime.now(timezone.utc).replace(tzinfo=None)
    ):
        return jsonify({"message": "Verification link has expired"}), 400

    user.is_verified = True
    user.verification_token_hash = None
    user.verification_token_expires_at = None

    db.session.commit()

    return jsonify({"message": "Email verified successfully"}), 200


# Log in an existing user
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    if not user.is_verified:
        return jsonify({
            "message": "Please verify your email before logging in"
        }), 403

    token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }), 200


# Get the logged-in user's profile
@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    user = g.current_user

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_verified": user.is_verified,
        "is_admin": user.is_admin,
        "created_at": (
            user.created_at.isoformat() if user.created_at else None
        )
    }), 200


# Update the logged-in user's profile
@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Request data is required"}), 400

    user = g.current_user

    if "name" in data:
        name = data["name"]

        if not isinstance(name, str) or not name.strip():
            return jsonify({"message": "Name cannot be empty"}), 400

        user.name = name.strip()

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_verified": user.is_verified,
            "is_admin": user.is_admin
        }
    }), 200
