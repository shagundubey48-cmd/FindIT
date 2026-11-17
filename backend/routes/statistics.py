from datetime import datetime, timezone

from flask import Blueprint, jsonify, g

from models.item import Item
from models.claim import Claim
from models.handover import Handover
from models.feedback import Feedback
from utils.auth_middleware import token_required


statistics_bp = Blueprint("statistics", __name__)

TREND_MONTHS = 6


def percentage(part, whole):
    return round(part / whole * 100, 1) if whole else 0.0


def last_months(count):
    """Return the last `count` months as 'YYYY-MM', oldest first."""
    now = datetime.now(timezone.utc)
    year, month = now.year, now.month
    months = []

    for _ in range(count):
        months.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    return list(reversed(months))


def month_key(value):
    return f"{value.year:04d}-{value.month:02d}" if value else None


def basic_figures():
    total_lost = Item.query.filter_by(item_type="lost").count()
    total_found = Item.query.filter_by(item_type="found").count()

    recovered = Handover.query.count()

    return {
        "total_lost_reports": total_lost,
        "total_found_reports": total_found,
        "items_recovered": recovered,
        # Share of found items that reached their owner.
        "recovery_rate": percentage(recovered, total_found),
        "active_items": Item.query.filter_by(status="active").count()
    }


@statistics_bp.route("/statistics/summary", methods=["GET"])
@token_required
def get_public_summary():
    """Headline figures any logged-in student can see."""
    return jsonify(basic_figures()), 200


@statistics_bp.route("/admin/statistics", methods=["GET"])
@token_required
def get_recovery_statistics():
    """Detailed recovery statistics for administrators."""

    if not g.current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403

    figures = basic_figures()

    # Claim outcomes
    approved = Claim.query.filter_by(status="approved").count()
    rejected = Claim.query.filter_by(status="rejected").count()
    pending = Claim.query.filter_by(status="pending").count()

    figures["claims"] = {
        "total": approved + rejected + pending,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "approval_rate": percentage(approved, approved + rejected)
    }

    # Average time between a found report and its handover
    handovers = Handover.query.all()
    durations = []

    for handover in handovers:
        created_at = handover.item.created_at

        if created_at and handover.handed_over_at:
            delta = handover.handed_over_at - created_at
            durations.append(max(delta.total_seconds(), 0) / 86400)

    figures["average_recovery_days"] = (
        round(sum(durations) / len(durations), 1) if durations else None
    )

    # Found vs recovered items per category
    recovered_item_ids = {handover.item_id for handover in handovers}
    categories = {}

    for item in Item.query.filter_by(item_type="found").all():
        entry = categories.setdefault(
            item.category,
            {"category": item.category, "found": 0, "recovered": 0}
        )
        entry["found"] += 1

        if item.id in recovered_item_ids:
            entry["recovered"] += 1

    by_category = sorted(
        categories.values(),
        key=lambda entry: entry["found"],
        reverse=True
    )

    for entry in by_category:
        entry["recovery_rate"] = percentage(
            entry["recovered"], entry["found"]
        )

    figures["by_category"] = by_category

    # Monthly trend
    months = last_months(TREND_MONTHS)
    trend = {m: {"month": m, "reports": 0, "recoveries": 0} for m in months}

    for item in Item.query.all():
        key = month_key(item.created_at)
        if key in trend:
            trend[key]["reports"] += 1

    for handover in handovers:
        key = month_key(handover.handed_over_at)
        if key in trend:
            trend[key]["recoveries"] += 1

    figures["monthly_trend"] = [trend[m] for m in months]

    # Feedback
    ratings = [feedback.rating for feedback in Feedback.query.all()]

    figures["feedback"] = {
        "count": len(ratings),
        "average_rating": (
            round(sum(ratings) / len(ratings), 2) if ratings else None
        )
    }

    return jsonify(figures), 200
