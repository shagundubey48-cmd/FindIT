"""Insert clearly labelled, fictional FindIT demo reports.

Run from the backend directory:
    python seed_demo_data.py

Safe to rerun: it exits if demo reports already exist.
"""
from datetime import date
import secrets

from werkzeug.security import generate_password_hash

from app import create_app, db
from models.user import User
from models.item import Item


DEMO_USERS = [
    ("Aarav Sharma", "demo.aarav@mail.jiit.ac.in"),
    ("Ananya Verma", "demo.ananya@mail.jiit.ac.in"),
    ("Rohan Gupta", "demo.rohan@mail.jiit.ac.in"),
]

DEMO_ITEMS = [
    {
        "owner": "demo.aarav@mail.jiit.ac.in",
        "title": "Black wireless earbuds case",
        "description": "Black charging case with a small scratch on the lid. DEMO SAMPLE — fictional report for presentation; not a real lost item.",
        "category": "Electronics",
        "campus": "JIIT Sector 62",
        "location": "Central Library, reading area",
        "item_type": "lost",
        "item_date": date(2026, 11, 17),
    },
    {
        "owner": "demo.ananya@mail.jiit.ac.in",
        "title": "Blue water bottle",
        "description": "Matte blue steel bottle with a white sticker. DEMO SAMPLE — fictional report for presentation; not a real lost item.",
        "category": "Other",
        "campus": "JIIT Sector 62",
        "location": "Cafeteria",
        "item_type": "lost",
        "item_date": date(2026, 11, 18),
    },
    {
        "owner": "demo.rohan@mail.jiit.ac.in",
        "title": "Student notebook",
        "description": "A5 ruled notebook with a green cover. DEMO SAMPLE — fictional report for presentation; not a real lost item.",
        "category": "Stationery",
        "campus": "JIIT Sector 128",
        "location": "Academic Block, classroom corridor",
        "item_type": "lost",
        "item_date": date(2026, 11, 16),
    },
    {
        "owner": "demo.aarav@mail.jiit.ac.in",
        "title": "Black college backpack",
        "description": "Medium black backpack with two front pockets. DEMO SAMPLE — fictional report for presentation; not a real lost item.",
        "category": "Bags",
        "campus": "JIIT Sector 128",
        "location": "Computer Science lab",
        "item_type": "lost",
        "item_date": date(2026, 11, 15),
    },
    {
        "owner": "demo.ananya@mail.jiit.ac.in",
        "title": "Silver wrist watch",
        "description": "Silver analogue watch with a round dial. DEMO SAMPLE — fictional report for presentation; not a real lost item.",
        "category": "Accessories",
        "campus": "JIIT Sector 62",
        "location": "Auditorium entrance",
        "item_type": "lost",
        "item_date": date(2026, 11, 17),
    },
    {
        "owner": "demo.rohan@mail.jiit.ac.in",
        "title": "USB-C laptop charger",
        "description": "White USB-C charger, approximately 65W. DEMO SAMPLE — fictional report for presentation; not a real lost item.",
        "category": "Electronics",
        "campus": "JIIT Sector 62",
        "location": "Electronics lab",
        "item_type": "lost",
        "item_date": date(2026, 11, 18),
    },
    {
        "owner": "demo.ananya@mail.jiit.ac.in",
        "title": "Grey hoodie",
        "description": "Plain grey hoodie, size medium. DEMO SAMPLE — fictional report for presentation; not a real found item.",
        "category": "Clothing",
        "campus": "JIIT Sector 62",
        "location": "Sports ground seating",
        "item_type": "found",
        "item_date": date(2026, 11, 18),
    },
    {
        "owner": "demo.rohan@mail.jiit.ac.in",
        "title": "Set of two keys",
        "description": "Two metal keys on a small blue keyring. DEMO SAMPLE — fictional report for presentation; not a real found item.",
        "category": "Accessories",
        "campus": "JIIT Sector 128",
        "location": "Main reception",
        "item_type": "found",
        "item_date": date(2026, 11, 17),
    },
    {
        "owner": "demo.aarav@mail.jiit.ac.in",
        "title": "透明 spectacles case",
        "description": "Clear hard-shell spectacles case. DEMO SAMPLE — fictional report for presentation; not a real found item.",
        "category": "Accessories",
        "campus": "JIIT Sector 62",
        "location": "Cafeteria, near water station",
        "item_type": "found",
        "item_date": date(2026, 11, 16),
    },
    {
        "owner": "demo.ananya@mail.jiit.ac.in",
        "title": "Calculus textbook",
        "description": "Mathematics textbook with a blue cover. DEMO SAMPLE — fictional report for presentation; not a real found item.",
        "category": "Stationery",
        "campus": "JIIT Sector 128",
        "location": "Library issue counter",
        "item_type": "found",
        "item_date": date(2026, 11, 15),
    },
    {
        "owner": "demo.rohan@mail.jiit.ac.in",
        "title": "Brown leather wallet",
        "description": "Slim brown wallet; contents not disclosed. DEMO SAMPLE — fictional report for presentation; not a real found item.",
        "category": "Accessories",
        "campus": "JIIT Sector 62",
        "location": "Academic Block, ground floor",
        "item_type": "found",
        "item_date": date(2026, 11, 18),
    },
    {
        "owner": "demo.aarav@mail.jiit.ac.in",
        "title": "Blue USB flash drive",
        "description": "Small blue USB flash drive found near a computer desk. DEMO SAMPLE — fictional report for presentation; not a real found item.",
        "category": "Electronics",
        "campus": "JIIT Sector 128",
        "location": "Computer lab 2",
        "item_type": "found",
        "item_date": date(2026, 11, 17),
    },
]


def seed_demo_data():
    app = create_app()
    with app.app_context():
        if Item.query.filter(Item.description.like("%DEMO SAMPLE%")).first():
            print("Demo reports already exist. No changes made.")
            return

        users = {}
        for name, email in DEMO_USERS:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    name=name,
                    email=email,
                    password=generate_password_hash(secrets.token_urlsafe(32)),
                    is_verified=True,
                    is_admin=False,
                )
                db.session.add(user)
                db.session.flush()
            users[email] = user

        for record in DEMO_ITEMS:
            item = Item(
                user_id=users[record["owner"]].id,
                title=record["title"],
                description=record["description"],
                category=record["category"],
                campus=record["campus"],
                location=record["location"],
                item_type=record["item_type"],
                item_date=record["item_date"],
                status="active",
            )
            db.session.add(item)

        db.session.commit()
        print(f"Added {len(DEMO_ITEMS)} clearly labelled demo reports.")


if __name__ == "__main__":
    seed_demo_data()
