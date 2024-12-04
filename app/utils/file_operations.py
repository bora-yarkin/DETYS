import csv
import os
from flask import current_app
from app.models.event_feedback import EventFeedback


def export_event_feedback(event_id):
    feedbacks = EventFeedback.query.filter_by(event_id=event_id).all()
    filename = f"feedback_event_{event_id}.csv"
    filepath = os.path.join(current_app.config["EXPORT_FOLDER"], filename)

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["user_id", "user_email", "rating", "comment", "submitted_at"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for feedback in feedbacks:
            writer.writerow(
                {
                    "user_id": feedback.user_id,
                    "user_email": feedback.user.email,
                    "rating": feedback.rating,
                    "comment": feedback.comment or "",
                    "submitted_at": feedback.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
    return filepath
