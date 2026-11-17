
from app import create_app, db

# Import every model so SQLAlchemy registers all database tables.
from models.user import User
from models.item import Item
from models.claim import Claim
from models.notification import Notification
from models.item_secret import ItemSecret, SecretVerification
from models.handover import Handover
from models.feedback import Feedback
from models.conversation import Conversation, Message


def initialize_database():
    app = create_app()

    with app.app_context():
        # Create all missing tables without deleting existing data.
        db.create_all()

        print("FindIT database initialized successfully!")

        # Display the created table names.
        for table in db.metadata.sorted_tables:
            print(f"Created/verified: {table.name}")


if __name__ == "__main__":
    initialize_database()
