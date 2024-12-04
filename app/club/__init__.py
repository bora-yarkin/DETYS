from flask import Blueprint

club_bp = Blueprint("club", __name__, template_folder="templates")

from . import routes
