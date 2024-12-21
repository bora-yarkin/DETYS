import os
import csv
from datetime import datetime
from flask import current_app
from app.models import Event, EventFeedback, EventAttendance, User, Club
from app.core.extensions import db


def ensure_export_folder():
    export_folder = current_app.config.get("EXPORT_FOLDER")
    if not os.path.exists(export_folder):
        os.makedirs(export_folder, exist_ok=True)
    return export_folder


def export_event_feedback_to_csv(allowed_event_ids=None):
    export_folder = ensure_export_folder()
    filename = f"event_feedback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_folder, filename)

    query = db.session.query(EventFeedback, Event.title, User.username).join(Event, EventFeedback.event_id == Event.id).join(User, EventFeedback.user_id == User.id)
    if allowed_event_ids is not None:
        query = query.filter(Event.id.in_(allowed_event_ids))

    feedback_data = query.all()

    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Event Title", "Username", "Rating", "Comment", "Submitted At"])
        for fb, event_title, username in feedback_data:
            writer.writerow([event_title, username, fb.rating, fb.comment if fb.comment else "", fb.submitted_at.isoformat() if fb.submitted_at else ""])

    return filepath


def export_event_attendance_to_csv(allowed_event_ids=None):
    export_folder = ensure_export_folder()
    filename = f"event_attendance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_folder, filename)

    query = db.session.query(EventAttendance, Event.title, User.username, Club.name).join(Event, EventAttendance.event_id == Event.id).join(User, EventAttendance.user_id == User.id).join(Club, Event.club_id == Club.id)
    if allowed_event_ids is not None:
        query = query.filter(Event.id.in_(allowed_event_ids))

    attendance_data = query.all()

    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Event Title", "Club Name", "Username", "Status", "Registered At"])
        for attendance, event_title, username, club_name in attendance_data:
            writer.writerow([event_title, club_name, username, attendance.status, attendance.registered_at.isoformat() if attendance.registered_at else ""])
    return filepath
