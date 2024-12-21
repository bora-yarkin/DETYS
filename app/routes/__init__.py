from .auth_routes import auth_bp
from .club_routes import club_bp
from .event_routes import event_bp
from .main_routes import main_bp
from .report_routes import report_bp
from .poll_routes import poll_bp
from .search_routes import search_bp
from .club_forum_routes import forum_bp
from .event_resource_routes import resource_bp


def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(club_bp, url_prefix="/clubs")
    app.register_blueprint(event_bp, url_prefix="/events")
    app.register_blueprint(report_bp, url_prefix="/admin")
    app.register_blueprint(poll_bp, url_prefix="/polls")
    app.register_blueprint(search_bp, url_prefix="/search")
    app.register_blueprint(forum_bp, url_prefix="/forums")
    app.register_blueprint(resource_bp, url_prefix="/resources")
