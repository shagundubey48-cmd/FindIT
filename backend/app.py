
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import Config
from extensions import mail


db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    mail.init_app(app)

    from routes.auth import auth_bp
    from routes.items import items_bp
    from routes.image_matching import image_matching_bp
    from routes.combined_matching import combined_matching_bp
    from routes.notifications import notifications_bp
    from routes.claims import claims_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(items_bp, url_prefix="/api")
    app.register_blueprint(image_matching_bp, url_prefix="/api")
    app.register_blueprint(combined_matching_bp, url_prefix="/api")
    app.register_blueprint(notifications_bp, url_prefix="/api")
    app.register_blueprint(claims_bp, url_prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
