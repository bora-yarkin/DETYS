from flask import Blueprint, request, render_template
from app.models import Club, Event, Post
from app.core.extensions import db

# Arama ile ilgili rotaları tanımlamak için Blueprint oluşturur
search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
def search():
    # Sorgu parametresinden arama terimini alır
    query = request.args.get("q", "")
    clubs = []
    events = []
    posts = []
    if query:
        # Kulüpleri isim veya açıklamaya göre arar
        clubs = Club.query.filter(Club.name.ilike(f"%{query}%") | Club.description.ilike(f"%{query}%")).all()
        # Etkinlikleri başlık veya açıklamaya göre arar
        events = Event.query.filter(Event.title.ilike(f"%{query}%") | Event.description.ilike(f"%{query}%")).all()
        # Gönderileri başlık veya içeriğe göre arar
        posts = Post.query.filter(Post.title.ilike(f"%{query}%") | Post.content.ilike(f"%{query}%")).all()

    # Arama sonuçlarını search/results.html şablonuna gönderir
    return render_template("search/results.html", query=query, clubs=clubs, events=events, posts=posts)
