from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.decorators import club_manager_required

club_bp = Blueprint("club", __name__, url_prefix="/clubs")


@club_bp.route("/manage")
@login_required
@club_manager_required
def manage_clubs():
    # Club management code
    pass
