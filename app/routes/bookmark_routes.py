# app/routes/bookmark_routes.py

from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from app.core.extensions import db
from app.models import Bookmark, Event, Club

bookmark_bp = Blueprint("bookmark", __name__)


@bookmark_bp.route("/club/<int:club_id>/add")
@login_required
def add_club_bookmark(club_id):
    existing = Bookmark.query.filter_by(user_id=current_user.id, club_id=club_id).first()
    if existing:
        flash("You already bookmarked this club.", "info")
    else:
        bookmark = Bookmark(user_id=current_user.id, club_id=club_id)
        db.session.add(bookmark)
        db.session.commit()
        flash("Club bookmarked!", "success")
    return redirect(url_for("club.club_detail", club_id=club_id))


@bookmark_bp.route("/club/<int:club_id>/remove")
@login_required
def remove_club_bookmark(club_id):
    bm = Bookmark.query.filter_by(user_id=current_user.id, club_id=club_id).first()
    if bm:
        db.session.delete(bm)
        db.session.commit()
        flash("Bookmark removed.", "success")
    return redirect(url_for("club.club_detail", club_id=club_id))


@bookmark_bp.route("/event/<int:event_id>/add")
@login_required
def add_event_bookmark(event_id):
    existing = Bookmark.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing:
        flash("You already bookmarked this event.", "info")
    else:
        bookmark = Bookmark(user_id=current_user.id, event_id=event_id)
        db.session.add(bookmark)
        db.session.commit()
        flash("Event bookmarked!", "success")
    return redirect(url_for("event.event_detail", event_id=event_id))


@bookmark_bp.route("/event/<int:event_id>/remove")
@login_required
def remove_event_bookmark(event_id):
    bm = Bookmark.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if bm:
        db.session.delete(bm)
        db.session.commit()
        flash("Bookmark removed.", "success")
    return redirect(url_for("event.event_detail", event_id=event_id))
