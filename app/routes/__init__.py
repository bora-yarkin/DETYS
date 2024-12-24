from .auth_routes import auth_bp
from .club_routes import club_bp
from .event_routes import event_bp
from .main_routes import main_bp
from .report_routes import report_bp
from .poll_routes import poll_bp
from .search_routes import search_bp
from .event_resource_routes import resource_bp
from .bookmark_routes import bookmark_bp
from .category_routes import category_bp
from .post_routes import post_bp


def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(club_bp, url_prefix="/clubs")
    app.register_blueprint(event_bp, url_prefix="/events")
    app.register_blueprint(report_bp, url_prefix="/admin")
    app.register_blueprint(poll_bp, url_prefix="/polls")
    app.register_blueprint(search_bp, url_prefix="/search")
    app.register_blueprint(resource_bp, url_prefix="/resources")
    app.register_blueprint(bookmark_bp, url_prefix="/bookmarks")
    app.register_blueprint(category_bp, url_prefix="/admin")
