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


def export_to_csv(filename_prefix, headers, query, row_formatter):
    export_folder = ensure_export_folder()
    filename = f"{filename_prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_folder, filename)

    data = query.all()

    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row_formatter(row))

    return filepath


def export_event_feedback_to_csv(allowed_event_ids=None):
    query = db.session.query(EventFeedback, Event.title, User.username).join(Event, EventFeedback.event_id == Event.id).join(User, EventFeedback.user_id == User.id)
    if allowed_event_ids is not None:
        query = query.filter(Event.id.in_(allowed_event_ids))

    headers = ["Event Title", "Username", "Rating", "Comment", "Submitted At"]
    row_formatter = lambda row: [row[1], row[2], row[0].rating, row[0].comment if row[0].comment else "", row[0].submitted_at.isoformat() if row[0].submitted_at else ""]

    return export_to_csv("event_feedback", headers, query, row_formatter)


def export_event_attendance_to_csv(allowed_event_ids=None):
    query = db.session.query(EventAttendance, Event.title, User.username, Club.name).join(Event, EventAttendance.event_id == Event.id).join(User, EventAttendance.user_id == User.id).join(Club, Event.club_id == Club.id)
    if allowed_event_ids is not None:
        query = query.filter(Event.id.in_(allowed_event_ids))

    headers = ["Event Title", "Club Name", "Username", "Status", "Registered At"]
    row_formatter = lambda row: [row[1], row[3], row[2], row[0].status, row[0].registered_at.isoformat() if row[0].registered_at else ""]

    return export_to_csv("event_attendance", headers, query, row_formatter)


def export_event_stats_to_csv(event_stats):
    headers = ["Metric", "Value"]
    rows = [["Total Events", event_stats["total_events"]], ["Average Attendance", f"{event_stats['average_attendance']:.2f}"]] + [["Category: " + cat, count] for cat, count in event_stats["event_by_category"]]

    return export_to_csv("event_stats", headers, rows, lambda x: x)


def export_user_stats_to_csv(user_stats):
    headers = ["Metric", "Value"]
    rows = [["Total Users", user_stats["total_users"]], ["Active Users (30 days)", user_stats["active_users"]], ["New Users (30 days)", user_stats["new_users"]], ["Average Events per User", f"{user_stats['average_events_per_user']:.2f}"]]

    return export_to_csv("user_stats", headers, rows, lambda x: x)


def export_club_stats_to_csv(club_stats):
    headers = ["Metric", "Value"]
    rows = [["Total Clubs", club_stats["total_clubs"]], ["Average Members per Club", f"{club_stats['avg_members']:.2f}"]] + [["Most Active: " + club, count] for club, count in club_stats["most_active_clubs"]]

    return export_to_csv("club_stats", headers, rows, lambda x: x)
