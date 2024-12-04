import os
from flask import Blueprint, render_template, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from flask_socketio import emit
from app import db
from app.models.event import Event
from app.models.club import Club
from app.models.event_attendance import EventAttendance
from app.models.event_feedback import EventFeedback
from app.forms import EventForm, EventFeedbackForm
from app.utils.decorators import club_manager_required, student_required
from app.utils.file_operations import export_event_feedback

event_bp = Blueprint("event", __name__, url_prefix="/events")


@event_bp.route("/")
def event_list():
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template("events/event_list.html", events=events)


@event_bp.route("/create/<int:club_id>", methods=["GET", "POST"])
@login_required
@club_manager_required
def create_event(club_id):
    club = Club.query.get_or_404(club_id)
    if club.president_id != current_user.id:
        abort(403)
    form = EventForm()
    if form.validate_on_submit():
        event = Event(title=form.title.data, description=form.description.data, date=form.date.data, location=form.location.data, capacity=form.capacity.data, club_id=club.id)
        db.session.add(event)
        db.session.commit()
        flash(f"Event '{event.title}' created successfully!", "success")
        return redirect(url_for("event.event_list"))
    return render_template("events/create_event.html", form=form, club=club)


@event_bp.route("/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    is_registered = False
    status = None
    can_provide_feedback = False
    feedback_submitted = False
    average_rating = None

    if current_user.is_authenticated:
        attendance = EventAttendance.query.filter_by(user_id=current_user.id, event_id=event.id).first()
        if attendance:
            is_registered = True
            status = attendance.status
            if attendance.status == "confirmed":
                existing_feedback = EventFeedback.query.filter_by(user_id=current_user.id, event_id=event.id).first()
                if existing_feedback:
                    feedback_submitted = True
                else:
                    can_provide_feedback = True

    average_rating = db.session.query(db.func.avg(EventFeedback.rating)).filter_by(event_id=event.id).scalar()
    if average_rating:
        average_rating = round(average_rating, 1)

    return render_template(
        "events/event_detail.html",
        event=event,
        is_registered=is_registered,
        status=status,
        can_provide_feedback=can_provide_feedback,
        feedback_submitted=feedback_submitted,
        average_rating=average_rating,
    )


@event_bp.route("/<int:event_id>/export_feedback")
@login_required
@club_manager_required
def export_feedback(event_id):
    event = Event.query.get_or_404(event_id)
    if event.club.president_id != current_user.id:
        abort(403)

    filepath = export_event_feedback(event_id)
    filename = os.path.basename(filepath)
    return send_file(filepath, as_attachment=True)


@event_bp.route("/<int:event_id>/register")
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    existing_attendance = EventAttendance.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if existing_attendance:
        flash("You have already registered for this event.", "info")
    else:
        confirmed_attendees = EventAttendance.query.filter_by(event_id=event.id, status="confirmed").count()
        if confirmed_attendees < event.capacity:
            status = "confirmed"
            flash("You have successfully registered for the event.", "success")
        else:
            status = "waiting"
            flash("The event is full. You have been added to the waiting list.", "info")
        attendance = EventAttendance(user_id=current_user.id, event_id=event.id, status=status)
        db.session.add(attendance)
        db.session.commit()
    return redirect(url_for("event.event_detail", event_id=event_id))


@event_bp.route("/<int:event_id>/feedback", methods=["GET", "POST"])
@login_required
@student_required
def submit_feedback(event_id):
    event = Event.query.get_or_404(event_id)

    # Check if the user attended the event
    attendance = EventAttendance.query.filter_by(user_id=current_user.id, event_id=event.id, status="confirmed").first()
    if not attendance:
        flash("You can only provide feedback for events you attended.", "warning")
        return redirect(url_for("event.event_detail", event_id=event_id))

    # Check if feedback already submitted
    existing_feedback = EventFeedback.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if existing_feedback:
        flash("You have already submitted feedback for this event.", "info")
        return redirect(url_for("event.event_detail", event_id=event_id))

    form = EventFeedbackForm(event_id=event_id)
    if form.validate_on_submit():
        feedback = EventFeedback(
            event_id=event.id,
            user_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data,
        )
        db.session.add(feedback)
        db.session.commit()
        flash("Thank you for your feedback!", "success")
        return redirect(url_for("event.event_detail", event_id=event_id))

    return render_template("events/submit_feedback.html", form=form, event=event)


@event_bp.route("/<int:event_id>/manage")
@login_required
@club_manager_required
def manage_event_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    if event.club.president_id != current_user.id:
        abort(403)
    confirmed_attendees = EventAttendance.query.filter_by(event_id=event.id, status="confirmed").all()
    waiting_attendees = EventAttendance.query.filter_by(event_id=event.id, status="waiting").all()
    return render_template("events/manage_attendees.html", event=event, confirmed_attendees=confirmed_attendees, waiting_attendees=waiting_attendees)


@event_bp.route("/<int:event_id>/cancel_registration")
@login_required
def cancel_registration(event_id):
    event = Event.query.get_or_404(event_id)
    attendance = EventAttendance.query.filter_by(user_id=current_user.id, event_id=event.id).first_or_404()
    db.session.delete(attendance)
    db.session.commit()
    flash("Your registration has been canceled.", "info")
    update_waiting_list(event)
    return redirect(url_for("event.event_detail", event_id=event_id))


def update_waiting_list(event):
    confirmed_attendees = EventAttendance.query.filter_by(event_id=event.id, status="confirmed").count()
    if confirmed_attendees < event.capacity:
        next_in_line = EventAttendance.query.filter_by(event_id=event.id, status="waiting").order_by(EventAttendance.registered_at.asc()).first()
        if next_in_line:
            next_in_line.status = "confirmed"
            db.session.commit()
            message = f"You have been moved from the waiting list to confirmed attendees for the event '{event.title}'."
            emit("notification", {"msg": message}, room=f"user_{next_in_line.user_id}")
