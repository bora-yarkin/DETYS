from .auth_routes import auth_bp
from .club_routes import club_bp
from .event_routes import event_bp
from .main_routes import main_bp


def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(club_bp, url_prefix="/clubs")
    app.register_blueprint(event_bp, url_prefix="/events")
