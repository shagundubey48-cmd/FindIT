
from datetime import datetime, timedelta, timezone
from io import BytesIO

import jwt
from werkzeug.security import generate_password_hash

from app import db
from models.user import User
from models.item import Item


# Create a verified user and authentication token
def create_authenticated_user():
    user = User(
        name="Test Student",
        email="student@mail.jiit.ac.in",
        password=generate_password_hash("Test@123"),
        is_verified=True
    )

    db.session.add(user)
    db.session.commit()

    token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        },
        "test-secret",
        algorithm="HS256"
    )

    return user, token


# Create an item belonging to a user
def create_test_item(user):
    item = Item(
        user_id=user.id,
        title="Black Wallet",
        description="Black leather wallet",
        category="Accessories",
        campus="JIIT Sector 62",
        location="Library",
        item_type="lost",
        item_date=datetime.strptime("2026-11-15", "%Y-%m-%d").date(),
        status="active"
    )

    db.session.add(item)
    db.session.commit()

    return item


# Check successful image upload
def test_image_upload_success(client, monkeypatch):
    user, token = create_authenticated_user()
    item = create_test_item(user)

    # Mock Cloudinary response
    monkeypatch.setattr(
        "routes.items.upload_item_image",
        lambda image: "https://res.cloudinary.com/demo/image/upload/test.jpg"
    )

    response = client.post(
        f"/api/items/{item.id}/image",
        data={
            "image": (BytesIO(b"fake image data"), "wallet.jpg")
        },
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["image_url"].endswith("test.jpg")

    db.session.refresh(item)
    assert item.image_url.endswith("test.jpg")


# Reject image upload without authentication
def test_image_upload_without_token(client):
    response = client.post(
        "/api/items/1/image",
        data={
            "image": (BytesIO(b"fake image data"), "wallet.jpg")
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 401


# Reject image upload without a file
def test_image_upload_without_file(client):
    user, token = create_authenticated_user()
    item = create_test_item(user)

    response = client.post(
        f"/api/items/{item.id}/image",
        data={},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


# Reject unsupported file formats
def test_image_upload_invalid_format(client):
    user, token = create_authenticated_user()
    item = create_test_item(user)

    response = client.post(
        f"/api/items/{item.id}/image",
        data={
            "image": (BytesIO(b"fake file data"), "document.pdf")
        },
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


# Prevent users from uploading images to another user's item
def test_image_upload_for_another_users_item(client):
    owner, owner_token = create_authenticated_user()
    item = create_test_item(owner)

    db.session.add(User(
        name="Another Student",
        email="another@mail.jiit.ac.in",
        password=generate_password_hash("Test@123"),
        is_verified=True
    ))
    db.session.commit()

    other_token = jwt.encode(
        {
            "sub": str(User.query.filter_by(
                email="another@mail.jiit.ac.in"
            ).first().id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        },
        "test-secret",
        algorithm="HS256"
    )

    response = client.post(
        f"/api/items/{item.id}/image",
        data={
            "image": (BytesIO(b"fake image data"), "wallet.jpg")
        },
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {other_token}"}
    )

    assert response.status_code == 404


# Handle Cloudinary upload failure
def test_image_upload_cloudinary_failure(client, monkeypatch):
    user, token = create_authenticated_user()
    item = create_test_item(user)

    def failed_upload(image):
        raise Exception("Cloudinary unavailable")

    monkeypatch.setattr(
        "routes.items.upload_item_image",
        failed_upload
    )

    response = client.post(
        f"/api/items/{item.id}/image",
        data={
            "image": (BytesIO(b"fake image data"), "wallet.jpg")
        },
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 502

