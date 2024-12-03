from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

from app.extensions import socketio
from instance.config import Config


# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
    app.config.from_object(Config)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app)  # Initialize SocketIO

    from app.controllers.main_controller import main_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.club_controller import club_bp
    from app.controllers.event_controller import event_bp
    from app.controllers.notification_controller import notification_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(club_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(notification_bp)

    # Import SocketIO event handlers
    from app.sockets import notification_socket

    return app


# User loader callback for Flask-Login
"""DO NOT MOVE TO TOP OF FILE"""
from app.models.user import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
