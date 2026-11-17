
from io import BytesIO

import requests
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


MODEL_NAME = "openai/clip-vit-base-patch32"

_model = None
_processor = None


def load_clip_model():
    """Load the pretrained CLIP model once and reuse it."""
    global _model, _processor

    if _model is None or _processor is None:
        _processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        _model = CLIPModel.from_pretrained(MODEL_NAME)
        _model.eval()

    return _model, _processor


def download_image(image_url):
    """Download an image and convert it to RGB format."""
    response = requests.get(image_url, timeout=20)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))
    return image.convert("RGB")


def get_image_embedding(image_url):
    """Convert an item image into a CLIP feature vector."""
    model, processor = load_clip_model()
    image = download_image(image_url)

    inputs = processor(images=image, return_tensors="pt")

    with torch.inference_mode():
        features = model.get_image_features(
            pixel_values=inputs["pixel_values"]
        )
        features = F.normalize(features, p=2, dim=-1)

    return features


def calculate_image_similarity(image_url1, image_url2):
    """Calculate visual similarity between two item images."""
    embedding1 = get_image_embedding(image_url1)
    embedding2 = get_image_embedding(image_url2)

    similarity = F.cosine_similarity(
        embedding1,
        embedding2,
        dim=-1
    ).item()

    # Convert cosine similarity into a percentage.
    score = max(0, min(100, similarity * 100))

    return round(score, 2)

