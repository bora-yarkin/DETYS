from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.core.extensions import db
from app.models import Event, Poll, PollChoice
from app.core.decorators import admin_or_manager_required

poll_bp = Blueprint("poll", __name__)


@poll_bp.route("/<int:event_id>/create", methods=["GET", "POST"])
@login_required
@admin_or_manager_required
def create_poll(event_id):
    event = Event.query.get_or_404(event_id)
    if event.club.president_id != current_user.id and not current_user.is_main_admin:
        flash("You don't have permission to create a poll for this event.", "danger")
        return redirect(url_for("event.event_detail", event_id=event.id))

    if request.method == "POST":
        question = request.form.get("question")
        choices = request.form.getlist("choice[]")
        if not question.strip():
            flash("Poll question is required.", "danger")
            return redirect(request.url)
        new_poll = Poll(event_id=event_id, question=question.strip())
        db.session.add(new_poll)
        db.session.flush()

        for text in choices:
            text = text.strip()
            if text:
                db.session.add(PollChoice(poll_id=new_poll.id, choice_text=text))

        db.session.commit()
        flash("Poll created successfully!", "success")
        return redirect(url_for("event.event_detail", event_id=event.id))

    return render_template("poll/create_poll.html", event=event)


@poll_bp.route("/<int:poll_id>")
@login_required
def view_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    event = Event.query.get_or_404(poll.event_id)
    total_votes = sum(choice.votes for choice in poll.choices)

    return render_template("poll/view_poll.html", poll=poll, event=event, total_votes=total_votes)


@poll_bp.route("/<int:poll_id>/vote", methods=["POST"])
@login_required
def vote_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    choice_id = request.form.get("choice_id")
    if not choice_id:
        flash("No choice selected.", "danger")
        return redirect(url_for("poll.view_poll", poll_id=poll.id))

    choice = PollChoice.query.filter_by(id=choice_id, poll_id=poll_id).first_or_404()
    choice.votes += 1
    db.session.commit()
    flash("Your vote has been recorded!", "success")
    return redirect(url_for("poll.view_poll", poll_id=poll.id))
