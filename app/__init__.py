from flask import Flask
from flask import Flask, render_template
from config import Config

# Initialize extensions
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO()
migrate = Migrate()


# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # Initialize extensions with the app
#     db.init_app(app)
#     login_manager.init_app(app)
#     mail.init_app(app)
#     socketio.init_app(app)
#     migrate.init_app(app, db)

#     # Register blueprints
#     from app.controllers.main_controller import main_bp

#     app.register_blueprint(main_bp)

#     return app


# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # Initialize extensions
#     db.init_app(app)
#     login_manager.init_app(app)
#     mail.init_app(app)
#     socketio.init_app(app)
#     migrate.init_app(app, db)

#     # Register blueprints
#     from app.controllers.main_controller import main_bp
#     from app.controllers.auth_controller import auth_bp

#     app.register_blueprint(main_bp)
#     app.register_blueprint(auth_bp)
#     return app


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.controllers.main_controller import main_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.club_controller import club_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(club_bp)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    return app
