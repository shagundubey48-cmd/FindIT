
import re
from difflib import SequenceMatcher
from models.item import Item


def normalize_text(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def calculate_similarity(text1, text2):
    words1 = normalize_text(text1)
    words2 = normalize_text(text2)

    if not words1 or not words2:
        return 0

    if not words1.intersection(words2):
        return 0

    overlap = len(words1.intersection(words2))
    union = len(words1.union(words2))

    jaccard_score = overlap / union
    sequence_score = SequenceMatcher(
        None,
        " ".join(sorted(words1)),
        " ".join(sorted(words2))
    ).ratio()

    return max(jaccard_score, sequence_score)


def calculate_match_score(item1, item2):
    title_score = calculate_similarity(item1.title, item2.title)
    description_score = calculate_similarity(
        item1.description, item2.description
    )

    category_score = (
        1 if item1.category.lower() == item2.category.lower() else 0
    )
    campus_score = (
        1 if item1.campus.lower() == item2.campus.lower() else 0
    )

    score = (
        title_score * 60
        + description_score * 20
        + category_score * 10
        + campus_score * 10
    )

    return round(score, 2)


def find_text_matches(item):
    opposite_type = "found" if item.item_type == "lost" else "lost"

    candidates = Item.query.filter(
        Item.item_type == opposite_type,
        Item.status == "active",
        Item.id != item.id,
        Item.user_id != item.user_id
    ).all()

    matches = []

    for candidate in candidates:
        title_score = calculate_similarity(
            item.title, candidate.title
        )
        description_score = calculate_similarity(
            item.description, candidate.description
        )

        # Require at least some title or description similarity.
        if title_score == 0 and description_score == 0:
            continue

        score = calculate_match_score(item, candidate)

        if score >= 20:
            matches.append({
                "item": candidate,
                "score": score
            })

    return sorted(
        matches,
        key=lambda match: match["score"],
        reverse=True
    )
