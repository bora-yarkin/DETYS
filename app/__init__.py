from flask import Flask
from instance.config import Config
from .extensions import db, login_manager, migrate, mail, socketio, csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app)
    csrf.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register blueprints
    from app.main import main_bp
    from app.auth import auth_bp
    from app.club import club_bp
    from app.event import event_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(club_bp, url_prefix="/clubs")
    app.register_blueprint(event_bp, url_prefix="/events")

    return app
