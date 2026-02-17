from .summarize_service import categorize_content
from ..models.database import db, Category
from datetime import datetime

COLORS = [
    "#EF4444",
    "#F97316",
    "#F59E0B",
    "#EAB308",
    "#84CC16",
    "#22C55E",
    "#10B981",
    "#14B8A6",
    "#06B6D4",
    "#0EA5E9",
    "#3B82F6",
    "#6366F1",
    "#8B5CF6",
    "#A855F7",
    "#D946EF",
    "#EC4899",
    "#F43F5E",
]


def get_or_create_category(category_name):
    category = Category.query.filter_by(name=category_name).first()

    if category:
        return category

    total_categories = Category.query.count()
    color = COLORS[total_categories % len(COLORS)]

    category = Category(
        name=category_name, description=f"Videos about {category_name}", color=color
    )

    db.session.add(category)
    db.session.commit()

    return category


def auto_categorize_video(title, summary):
    if not title and not summary:
        return None

    category_name = categorize_content(title, summary)
    category = get_or_create_category(category_name)

    return category
