from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.decorators import club_manager_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@main_bp.route("/club-manager-only")
@login_required
@club_manager_required
def club_manager_page():
    return "This page is only accessible to club managers."
