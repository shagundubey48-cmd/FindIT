import os
import certifi
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")

    ALLOWED_EMAIL_DOMAINS = ["mail.jiit.ac.in"]

    # MySQL / TiDB database connection
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "finditplus")

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Enable verified TLS for hosted TiDB connections
    if DB_HOST != "localhost" and DB_HOST != "127.0.0.1":
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "ssl_ca": certifi.where(),
                "ssl_verify_cert": True,
                "ssl_verify_identity": True
            },
            "pool_pre_ping": True
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True
        }

    # Gmail configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database="finditplus_test"
    )

    TESTING = True
    MAIL_SUPPRESS_SEND = True

    # The tests sign their own JWTs with this key, so it must not depend
    # on whatever SECRET_KEY happens to be in the developer's .env file.
    SECRET_KEY = "test-secret"
