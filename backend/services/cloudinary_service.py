
import cloudinary
import cloudinary.uploader
from flask import current_app


# Upload an image to Cloudinary and return its secure URL
def upload_item_image(image_file):
    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
        secure=True
    )

    result = cloudinary.uploader.upload(
        image_file,
        folder="finditplus/items",
        resource_type="image"
    )

    return result["secure_url"]

