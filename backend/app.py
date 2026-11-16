
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
    app.register_blueprint(auth_bp, url_prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
