
import os
from io import BytesIO

import requests
from PIL import Image

MODEL_NAME = "openai/clip-vit-base-patch32"

_model = None
_processor = None


def check_image_matching_enabled():
    if os.getenv("DISABLE_IMAGE_MATCHING", "false").lower() == "true":
        raise RuntimeError("Image matching is disabled on this server.")


def load_clip_model():
    global _model, _processor

    check_image_matching_enabled()

    if _model is None or _processor is None:
        from transformers import CLIPModel, CLIPProcessor

        _processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        _model = CLIPModel.from_pretrained(MODEL_NAME)
        _model.eval()

    return _model, _processor


def download_image(image_url):
    response = requests.get(image_url, timeout=20)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))
    return image.convert("RGB")


def get_image_embedding(image_url):
    model, processor = load_clip_model()

    import torch
    import torch.nn.functional as F

    image = download_image(image_url)
    inputs = processor(images=image, return_tensors="pt")

    with torch.inference_mode():
        features = model.get_image_features(
            pixel_values=inputs["pixel_values"]
        )
        features = F.normalize(features, p=2, dim=-1)

    return features


def calculate_image_similarity(image_url1, image_url2):
    check_image_matching_enabled()

    import torch
    import torch.nn.functional as F

    embedding1 = get_image_embedding(image_url1)
    embedding2 = get_image_embedding(image_url2)

    similarity = F.cosine_similarity(
        embedding1,
        embedding2,
        dim=-1
    ).item()

    score = max(0, min(100, similarity * 100))

    return round(score, 2)
