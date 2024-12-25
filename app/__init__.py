from flask import Flask
from app.core.config import Config
from app.core.extensions import db, login_manager, migrate, mail, csrf
from app.routes import register_routes
from flask_wtf.csrf import generate_csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # app.config["WTF_CSRF_ENABLED"] = False

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    register_routes(app)

    return app
