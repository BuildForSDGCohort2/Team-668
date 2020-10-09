import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = os.environ.get("ADMINS")
    POSTS_PER_PAGE = 15
    SHOPAISLES_PER_PAGE = 15
    PRODUCTS_PER_PAGE = 3
    CATEGORY_PER_PAGE = 15
    UPLOAD_FOLDER = "/app/static/uploads"
    ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}
    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, "app/static/images/profileImages")
    MAX_CONTENT_LENGTH = 1024 * 1024
    UPLOAD_EXTENSIONS = [".jpg", ".png", ".gif", ".png"]
    UPLOAD_PATH = "app/static/images/profileImages"
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")
    CLIENT_ID = (
        AUze3YRwyerbtTFKS00m3PTjynPSCF151q_WM4ChfcHFUea8pVc4ZcwWk8ZEvXeiSm2bWZjUho2e1VNg
    )
    APP_ID = 379583396787574

