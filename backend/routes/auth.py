
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from models.user import User
from app import db
from services.email_service import send_verification_email
from datetime import datetime, timedelta, timezone
import secrets
import hashlib
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

    # Check approved college email domain
    allowed_domains = current_app.config["ALLOWED_EMAIL_DOMAINS"]
    email_domain = email.rsplit("@", 1)[1]

    if email_domain not in allowed_domains:
        return jsonify({
            "message": "Please use your JIIT college email"
        }), 400

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

    # Generate secure verification token
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # Create unverified account
    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        is_verified=False,
        verification_token_hash=token_hash,
        verification_token_expires_at=(
            datetime.now(timezone.utc).replace(tzinfo=None)
            + timedelta(minutes=15)
        )
    )

    try:
        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        send_verification_email(email, token)

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already registered"}), 409

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Registration email could not be sent")
        return jsonify({
            "message": "Registration could not be completed"
        }), 500

    return jsonify({
        "message": "Registration successful. Please verify your email."
    }), 201


# Verify student email
@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):

    token_hash = hashlib.sha256(token.encode()).hexdigest()

    user = User.query.filter_by(
        verification_token_hash=token_hash
    ).first()

    if not user:
        return jsonify({
            "message": "Invalid verification link"
        }), 400

    if user.is_verified:
        return jsonify({
            "message": "Email already verified"
        }), 200

    expiry = user.verification_token_expires_at

    if not expiry or expiry <= datetime.now(timezone.utc).replace(tzinfo=None):
        return jsonify({
            "message": "Verification link expired"
        }), 400

    user.is_verified = True
    user.verification_token_hash = None
    user.verification_token_expires_at = None

    db.session.commit()

    return jsonify({
        "message": "Email verified successfully"
    }), 200
