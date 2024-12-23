import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key_here"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///detys.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    basedir = os.path.abspath(os.path.dirname(__file__))
    EXPORT_FOLDER = os.path.join(basedir, "../static/exports")
