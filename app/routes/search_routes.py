from flask import Blueprint, request, render_template
from app.models import Club, Event
from app.core.extensions import db

search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
def search():
    query = request.args.get("q", "")
    clubs = []
    events = []
    if query:
        # Basic example: search name/description
        clubs = Club.query.filter(Club.name.ilike(f"%{query}%") | Club.description.ilike(f"%{query}%")).all()
        events = Event.query.filter(Event.title.ilike(f"%{query}%") | Event.description.ilike(f"%{query}%")).all()

    return render_template("search/results.html", query=query, clubs=clubs, events=events)
