from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    CORS(app)

    db.init_app(app)

    from routes.auth import auth_bp
    from routes.items import items_bp
    from routes.image_matching import image_matching_bp
    from routes.combined_matching import combined_matching_bp
    from routes.notifications import notifications_bp
    from routes.claims import claims_bp
    from routes.admin import admin_bp
    from routes.handovers import handovers_bp
    from routes.feedback import feedback_bp
    from routes.secret_question import secret_question_bp
    from routes.qr_codes import qr_codes_bp
    from routes.messages import messages_bp
    from routes.unclaimed import unclaimed_bp
    from routes.statistics import statistics_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(items_bp, url_prefix="/api")
    app.register_blueprint(image_matching_bp, url_prefix="/api")
    app.register_blueprint(combined_matching_bp, url_prefix="/api")
    app.register_blueprint(notifications_bp, url_prefix="/api")
    app.register_blueprint(claims_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(handovers_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
    app.register_blueprint(secret_question_bp, url_prefix="/api")
    app.register_blueprint(qr_codes_bp, url_prefix="/api")
    app.register_blueprint(messages_bp, url_prefix="/api")
    app.register_blueprint(unclaimed_bp, url_prefix="/api")
    app.register_blueprint(statistics_bp, url_prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
