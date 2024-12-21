import base64
import matplotlib
import matplotlib.pyplot as plt
import os
from flask import Blueprint, render_template, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from io import BytesIO
from app.core.extensions import db
from app.models import Event, EventAttendance, EventFeedback, Club, User
from app.core.decorators import main_admin_required
from xhtml2pdf import pisa
from app.core.data_processing import export_event_feedback_to_csv, export_event_attendance_to_csv

matplotlib.use("Agg")

report_bp = Blueprint("report", __name__)


def get_event_ids_for_current_user():
    if hasattr(current_user, "is_main_admin") and current_user.is_main_admin:
        # Main admin → no filter
        all_events = Event.query.all()
        return [event.id for event in all_events]
    else:
        # Club manager → filter by clubs they manage
        clubs_managed = Club.query.filter_by(president_id=current_user.id).all()
        club_ids = [club.id for club in clubs_managed]

        # Gather the events that belong to these clubs
        managed_events = Event.query.filter(Event.club_id.in_(club_ids)).all()
        return [event.id for event in managed_events]


def generate_participation_chart(participation_data):
    if not participation_data:
        return None
    event_titles = [item[0] for item in participation_data]
    counts = [item[1] for item in participation_data]

    plt.figure(figsize=(8, 4))
    plt.bar(event_titles, counts, color="skyblue")
    plt.xlabel("Events")
    plt.ylabel("Number of Participants")
    plt.title("Event Participation")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png")
    plt.close()
    img_buffer.seek(0)
    return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")


@report_bp.route("/reports")
@login_required
def reports():
    allowed_event_ids = get_event_ids_for_current_user()

    participation_data = db.session.query(Event.title, db.func.count(EventAttendance.user_id)).join(EventAttendance, Event.id == EventAttendance.event_id).filter(EventAttendance.status == "confirmed", Event.id.in_(allowed_event_ids)).group_by(Event.id).all()

    feedback_data = db.session.query(Event.title, db.func.avg(EventFeedback.rating)).join(EventFeedback, Event.id == EventFeedback.event_id).filter(Event.id.in_(allowed_event_ids)).group_by(Event.id).all()

    sorted_by_popularity = sorted(participation_data, key=lambda x: x[1], reverse=True)[:5]
    base64_image = generate_participation_chart(participation_data)

    return render_template("report/report.html", participation_data=participation_data, sorted_by_popularity=sorted_by_popularity, feedback_data=feedback_data, base64_image=base64_image)


@report_bp.route("/reports/download_pdf")
@login_required
def download_pdf():
    allowed_event_ids = get_event_ids_for_current_user()

    participation_data = db.session.query(Event.title, db.func.count(EventAttendance.user_id)).join(EventAttendance, Event.id == EventAttendance.event_id).filter(EventAttendance.status == "confirmed", Event.id.in_(allowed_event_ids)).group_by(Event.id).all()

    feedback_data = db.session.query(Event.title, db.func.avg(EventFeedback.rating)).join(EventFeedback, Event.id == EventFeedback.event_id).filter(Event.id.in_(allowed_event_ids)).group_by(Event.id).all()

    base64_image = generate_participation_chart(participation_data)
    html = render_template("report/pdf_template.html", participation_data=participation_data, feedback_data=feedback_data, current_date=datetime.utcnow(), base64_image=base64_image)

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=pdf_buffer, encoding="utf-8")

    if pisa_status.err:
        return "Error generating PDF", 500

    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=True, download_name="report.pdf", mimetype="application/pdf")


@report_bp.route("/reports/export_feedback_csv")
@login_required
def export_feedback_csv():
    allowed_event_ids = get_event_ids_for_current_user()

    filepath = export_event_feedback_to_csv(allowed_event_ids=allowed_event_ids)
    if filepath:
        flash("Feedback CSV generated successfully!", "success")
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath), mimetype="text/csv")
    else:
        flash("Failed to generate feedback CSV.", "danger")
        return redirect(url_for("report.reports"))


@report_bp.route("/reports/export_attendance_csv")
@login_required
def export_attendance_csv():
    allowed_event_ids = get_event_ids_for_current_user()

    filepath = export_event_attendance_to_csv(allowed_event_ids=allowed_event_ids)
    if filepath:
        flash("Attendance CSV generated successfully!", "success")
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath), mimetype="text/csv")
    else:
        flash("Failed to generate attendance CSV.", "danger")
        return redirect(url_for("report.reports"))
