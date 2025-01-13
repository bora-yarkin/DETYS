from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from app.core.extensions import db
from app.models import Bookmark

bookmark_bp = Blueprint("bookmark", __name__)


# Kullanıcıya ait bir bookmark ekler
def add_bookmark(user_id, club_id=None, event_id=None):
    # Mevcut bookmark'ı kontrol eder
    existing = Bookmark.query.filter_by(user_id=user_id, club_id=club_id, event_id=event_id).first()
    if existing:
        flash("You already bookmarked this item.", "info")
    else:
        # Yeni bookmark oluşturur ve veritabanına ekler
        bookmark = Bookmark(user_id=user_id, club_id=club_id, event_id=event_id)
        db.session.add(bookmark)
        db.session.commit()
        flash("Item bookmarked!", "success")


# Kullanıcıya ait bir bookmark'ı kaldırır
def remove_bookmark(user_id, club_id=None, event_id=None):
    bm = Bookmark.query.filter_by(user_id=user_id, club_id=club_id, event_id=event_id).first()
    if bm:
        db.session.delete(bm)
        db.session.commit()
        flash("Bookmark removed.", "success")


# Kulüp bookmark ekleme işlemi
@bookmark_bp.route("/club/<int:club_id>/add")
@login_required
def add_club_bookmark(club_id):
    add_bookmark(current_user.id, club_id=club_id)
    return redirect(url_for("club.club_detail", club_id=club_id))


# Kulüp bookmark kaldırma işlemi
@bookmark_bp.route("/club/<int:club_id>/remove")
@login_required
def remove_club_bookmark(club_id):
    remove_bookmark(current_user.id, club_id=club_id)
    return redirect(url_for("club.club_detail", club_id=club_id))


# Etkinlik bookmark ekleme işlemi
@bookmark_bp.route("/event/<int:event_id>/add")
@login_required
def add_event_bookmark(event_id):
    add_bookmark(current_user.id, event_id=event_id)
    return redirect(url_for("event.event_detail", event_id=event_id))


# Etkinlik bookmark kaldırma işlemi
@bookmark_bp.route("/event/<int:event_id>/remove")
@login_required
def remove_event_bookmark(event_id):
    remove_bookmark(current_user.id, event_id=event_id)
    return redirect(url_for("event.event_detail", event_id=event_id))
