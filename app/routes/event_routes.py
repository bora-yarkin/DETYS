from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Event, EventAttendance, EventFeedback
from app.forms import EventForm, EventFeedbackForm
from app.core.extensions import db
from app.core.decorators import club_manager_required, student_required

event_bp = Blueprint("event", __name__)


@event_bp.route("/")
def event_list():
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template("event/event_list.html", events=events)


@event_bp.route("/create", methods=["GET", "POST"])
@login_required
@club_manager_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event_date = datetime.strptime(form.date.data, "%Y-%m-%dT%H:%M")
        event = Event(title=form.title.data, description=form.description.data, date=event_date, location=form.location.data, capacity=form.capacity.data, club_id=current_user.managed_club_id)
        db.session.add(event)
        db.session.commit()
        flash("Event created successfully!", "success")
        return redirect(url_for("event.event_list"))
    return render_template("event/create_event.html", form=form)


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
            if status == "confirmed":
                existing_feedback = EventFeedback.query.filter_by(user_id=current_user.id, event_id=event.id).first()
                if existing_feedback:
                    feedback_submitted = True
                else:
                    can_provide_feedback = True

    average_rating = db.session.query(db.func.avg(EventFeedback.rating)).filter_by(event_id=event.id).scalar()
    if average_rating:
        average_rating = round(average_rating, 1)

    return render_template("event/event_detail.html", event=event, is_registered=is_registered, status=status, can_provide_feedback=can_provide_feedback, feedback_submitted=feedback_submitted, average_rating=average_rating)


@event_bp.route("/<int:event_id>/cancel_registration")
@login_required
def cancel_registration(event_id):
    event = Event.query.get_or_404(event_id)
    attendance = EventAttendance.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if attendance:
        db.session.delete(attendance)
        db.session.commit()
        flash("Your registration has been canceled.", "success")
    else:
        flash("You are not registered for this event.", "warning")
    return redirect(url_for("event.event_detail", event_id=event_id))


@event_bp.route("/<int:event_id>/manage_attendees")
@login_required
@club_manager_required
def manage_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    confirmed_attendees = EventAttendance.query.filter_by(event_id=event.id, status="confirmed").all()
    waiting_attendees = EventAttendance.query.filter_by(event_id=event.id, status="waiting").all()
    return render_template("event/manage_attendees.html", event=event, confirmed_attendees=confirmed_attendees, waiting_attendees=waiting_attendees)


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
def submit_feedback(event_id):
    event = Event.query.get_or_404(event_id)
    attendance = EventAttendance.query.filter_by(user_id=current_user.id, event_id=event.id, status="confirmed").first()
    if not attendance:
        flash("You can only provide feedback for events you attended.", "warning")
        return redirect(url_for("event.event_detail", event_id=event_id))
    existing_feedback = EventFeedback.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if existing_feedback:
        flash("You have already submitted feedback for this event.", "info")
        return redirect(url_for("event.event_detail", event_id=event_id))
    form = EventFeedbackForm(event_id=event_id)
    if form.validate_on_submit():
        feedback = EventFeedback(event_id=event.id, user_id=current_user.id, rating=form.rating.data, comment=form.comment.data)
        db.session.add(feedback)
        db.session.commit()
        flash("Thank you for your feedback!", "success")
        return redirect(url_for("event.event_detail", event_id=event_id))
    return render_template("event/submit_feedback.html", form=form, event=event)
