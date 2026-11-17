
from app import db
from models.notification import Notification


def create_match_notifications(item, matched_item):
    """Notify both owners about a potential lost-and-found match."""

    # Store item IDs in a consistent order to prevent duplicate pairs.
    first_id = min(item.id, matched_item.id)
    second_id = max(item.id, matched_item.id)

    owners = {
        item.user_id: item,
        matched_item.user_id: matched_item
    }

    for user_id, reported_item in owners.items():
        existing = Notification.query.filter_by(
            user_id=user_id,
            item_id=first_id,
            matched_item_id=second_id
        ).first()

        if existing:
            continue

        other_item = (
            matched_item if reported_item.id == item.id else item
        )

        notification = Notification(
            user_id=user_id,
            item_id=first_id,
            matched_item_id=second_id,
            message=(
                f"A potential match was found for your item "
                f"'{reported_item.title}'. Matching item: "
                f"'{other_item.title}'."
            )
        )

        db.session.add(notification)

    db.session.commit()

