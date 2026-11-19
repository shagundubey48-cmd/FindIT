from functools import wraps

import jwt
from flask import request, jsonify, current_app, g

from app import db
from models.user import User


# Verify JWT and identify the logged-in user
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"message": "Authentication token is required"}), 401

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"message": "Invalid authorization header"}), 401

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            user = db.session.get(User, int(payload["sub"]))

            if not user:
                return jsonify({"message": "User not found"}), 401

            g.current_user = user

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, ValueError):
            return jsonify({"message": "Invalid or expired token"}), 401

        return func(*args, **kwargs)

    return decorated
