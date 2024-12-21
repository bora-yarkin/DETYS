from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.core.extensions import db
from app.models import Event, Poll, PollChoice

poll_bp = Blueprint("poll", __name__)


@poll_bp.route("/<int:event_id>/create", methods=["GET", "POST"])
@login_required
def create_poll(event_id):
    event = Event.query.get_or_404(event_id)
    if event.club.president_id != current_user.id and not current_user.is_main_admin:
        flash("You are not allowed to create a poll for this event.", "danger")
        return redirect(url_for("event.event_detail", event_id=event_id))

    if request.method == "POST":
        question = request.form.get("question")
        choices = request.form.getlist("choice[]")

        poll = Poll(event_id=event_id, question=question)
        db.session.add(poll)
        db.session.flush()

        for c in choices:
            if c.strip():
                db.session.add(PollChoice(poll_id=poll.id, choice_text=c.strip(), votes=0))
        db.session.commit()
        flash("Poll created successfully!", "success")
        return redirect(url_for("event.event_detail", event_id=event_id))

    return render_template("poll/create_poll.html", event=event)


@poll_bp.route("/<int:poll_id>/vote", methods=["POST"])
@login_required
def vote_poll(poll_id):
    choice_id = request.form.get("choice_id")
    choice = PollChoice.query.filter_by(id=choice_id, poll_id=poll_id).first_or_404()
    choice.votes += 1
    db.session.commit()
    flash("Your vote has been recorded!", "success")
    return redirect(url_for("poll.view_poll", poll_id=poll_id))


@poll_bp.route("/<int:poll_id>")
@login_required
def view_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    return render_template("poll/view_poll.html", poll=poll)
