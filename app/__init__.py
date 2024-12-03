from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from app.extensions import socketio

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app)  # Initialize SocketIO

    # Register blueprints
    from app.controllers.main_controller import main_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.club_controller import club_bp
    from app.controllers.event_controller import event_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(club_bp)
    app.register_blueprint(event_bp)

    # Import SocketIO event handlers
    # from app.sockets import notification_socket

    return app


# User loader callback for Flask-Login
from app.models.user import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
