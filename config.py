"""All settings for Foodie. Secrets are read from the .env file."""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "foodie")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "foods")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB image limit
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

    # Billing rules (rupees / percent)
    DELIVERY_FEE = 40
    FREE_DELIVERY_ABOVE = 500
    TAX_PERCENT = 5
    MAX_ITEM_QTY = 20

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
