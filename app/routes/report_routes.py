import os
import base64
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import matplotlib
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from xhtml2pdf import pisa

from app.core.extensions import db
from app.core.analytics import Analytics
from app.models import Category, Event, EventAttendance, EventFeedback, Club
from app.core.data_processing import export_event_feedback_to_csv, export_event_attendance_to_csv, export_event_stats_to_csv, export_user_stats_to_csv, export_club_stats_to_csv

matplotlib.use("Agg")

report_bp = Blueprint("report", __name__)


def get_event_ids_for_current_user():
    if hasattr(current_user, "is_main_admin") and current_user.is_main_admin:
        all_events = Event.query.all()
        return [event.id for event in all_events]
    else:
        clubs_managed = Club.query.filter_by(president_id=current_user.id).all()
        club_ids = [club.id for club in clubs_managed]

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


def generate_category_chart(data):
    plt.figure(figsize=(8, 4))
    plt.pie([x[1] for x in data], labels=[x[0] for x in data], autopct="%1.1f%%")
    plt.title("Events by Category")

    return convert_plot_to_base64()


def generate_rating_chart(data):
    plt.figure(figsize=(8, 4))
    plt.bar([str(x[0]) for x in data], [x[1] for x in data])
    plt.title("Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Count")

    return convert_plot_to_base64()


def generate_club_chart(data):
    plt.figure(figsize=(8, 4))
    plt.bar([x[0] for x in data], [x[1] for x in data])
    plt.title("Most Active Clubs")
    plt.xticks(rotation=45)

    return convert_plot_to_base64()


def convert_plot_to_base64():
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png", bbox_inches="tight")
    plt.close()
    img_buffer.seek(0)
    return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")


@report_bp.route("/reports")
@login_required
def reports():
    allowed_event_ids = get_event_ids_for_current_user()
    category_id = request.args.get("category_id", type=int)

    query = db.session.query(Event.title, func.count(EventAttendance.user_id)).join(EventAttendance).filter(EventAttendance.status == "confirmed", Event.id.in_(allowed_event_ids))

    if category_id:
        query = query.filter(Event.category_id == category_id)

    participation_data = query.group_by(Event.id, Event.title).all()

    analytics = Analytics()
    event_stats = analytics.get_event_stats()
    user_stats = analytics.get_user_stats()
    club_stats = analytics.get_club_stats()
    feedback_stats = analytics.get_feedback_stats()

    base64_charts = {
        "participation": generate_participation_chart(participation_data),
        "categories": generate_category_chart(event_stats["event_by_category"]),
        "ratings": generate_rating_chart(feedback_stats["rating_distribution"]),
        "club_activity": generate_club_chart(club_stats["most_active_clubs"]),
    }

    return render_template(
        "report/report.html", participation_data=participation_data, event_stats=event_stats, user_stats=user_stats, club_stats=club_stats, feedback_stats=feedback_stats, charts=base64_charts, categories=Category.query.order_by(Category.name.asc()).all(), selected_category_id=category_id
    )


@report_bp.route("/reports/download_pdf")
@login_required
def download_pdf():
    allowed_event_ids = get_event_ids_for_current_user()
    category_id = request.args.get("category_id", type=int)

    participation_query = db.session.query(Event.title, db.func.count(EventAttendance.user_id)).join(EventAttendance, Event.id == EventAttendance.event_id).filter(EventAttendance.status == "confirmed", Event.id.in_(allowed_event_ids))
    if category_id:
        participation_query = participation_query.filter(Event.category_id == category_id)
    participation_data = participation_query.group_by(Event.id).all()

    feedback_query = db.session.query(Event.title, db.func.avg(EventFeedback.rating)).join(EventFeedback, Event.id == EventFeedback.event_id).filter(Event.id.in_(allowed_event_ids))
    if category_id:
        feedback_query = feedback_query.filter(Event.category_id == category_id)
    feedback_data = feedback_query.group_by(Event.id).all()

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


@report_bp.route("/reports/export_stats_csv")
@login_required
def export_stats_csv():
    analytics = Analytics()
    event_stats = analytics.get_event_stats()
    user_stats = analytics.get_user_stats()
    club_stats = analytics.get_club_stats()

    # Export each stat type
    event_filepath = export_event_stats_to_csv(event_stats)
    user_filepath = export_user_stats_to_csv(user_stats)
    club_filepath = export_club_stats_to_csv(club_stats)

    if event_filepath and user_filepath and club_filepath:
        # Create zip file containing all stats
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.write(event_filepath, os.path.basename(event_filepath))
            zip_file.write(user_filepath, os.path.basename(user_filepath))
            zip_file.write(club_filepath, os.path.basename(club_filepath))

        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name=f"all_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip", mimetype="application/zip")

    flash("Failed to generate statistics files.", "danger")
    return redirect(url_for("report.reports"))
