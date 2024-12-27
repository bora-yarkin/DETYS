import os
import base64
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import matplotlib
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, and_
from xhtml2pdf import pisa

from app.core.extensions import db
from app.core.analytics import Analytics
from app.models import Category, Event, EventAttendance, EventFeedback, Club
from app.core.data_processing import export_event_feedback_to_csv, export_event_attendance_to_csv, export_event_stats_to_csv, export_user_stats_to_csv, export_club_stats_to_csv

matplotlib.use("Agg")

report_bp = Blueprint("report", __name__)


def get_event_ids_for_current_user():
    if getattr(current_user, "is_main_admin", False):
        return [e.id for e in Event.query.all()]
    clubs_managed = Club.query.filter_by(president_id=current_user.id).all()
    club_ids = [club.id for club in clubs_managed]
    return [e.id for e in Event.query.filter(Event.club_id.in_(club_ids)).all()]


def generate_participation_chart(participation_data):
    if not participation_data:
        return None
    titles = [item[0] for item in participation_data]
    counts = [item[1] for item in participation_data]
    plt.figure(figsize=(8, 4))
    plt.bar(titles, counts, color="skyblue")
    plt.xlabel("Events")
    plt.ylabel("Number of Participants")
    plt.title("Event Participation")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")


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
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")


@report_bp.route("/reports")
@login_required
def reports():
    allowed_event_ids = get_event_ids_for_current_user()

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    category_ids = request.args.getlist("category_ids", type=int)
    club_id = request.args.get("club_id", type=int)
    category_id = request.args.get("category_id", type=int)

    query = db.session.query(Event.title, func.count(EventAttendance.user_id)).join(EventAttendance).filter(EventAttendance.status == "confirmed", Event.id.in_(allowed_event_ids))

    if from_date:
        query = query.filter(Event.date >= from_date)
    if to_date:
        query = query.filter(Event.date <= to_date)

    if category_ids:
        query = query.filter(Event.category_id.in_(category_ids))

    if club_id:
        query = query.filter(Event.club_id == club_id)

    participation_data = query.group_by(Event.id, Event.title).all()

    popular_query = db.session.query(Event.title, func.count(EventAttendance.user_id).label("cnt")).join(EventAttendance).filter(EventAttendance.status == "confirmed", Event.id.in_(allowed_event_ids))
    if category_id:
        popular_query = popular_query.filter(Event.category_id == category_id)
    sorted_by_popularity = popular_query.group_by(Event.id, Event.title).order_by(func.count(EventAttendance.user_id).desc()).limit(5).all()

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

    feedback_data = db.session.query(Event.title, func.avg(EventFeedback.rating)).join(EventFeedback).filter(Event.id.in_(allowed_event_ids))
    if category_id:
        feedback_data = feedback_data.filter(Event.category_id == category_id)
    feedback_data = feedback_data.group_by(Event.id).all()

    return render_template(
        "report/report.html",
        participation_data=participation_data,
        sorted_by_popularity=sorted_by_popularity,
        feedback_data=feedback_data,
        event_stats=event_stats,
        user_stats=user_stats,
        club_stats=club_stats,
        feedback_stats=feedback_stats,
        charts=base64_charts,
        categories=Category.query.order_by(Category.name.asc()).all(),
        selected_category_id=category_id,
        from_date=from_date,
        to_date=to_date,
        selected_categories=category_ids,
        selected_club=club_id,
        clubs=Club.query.order_by(Club.name.asc()).all(),
    )


@report_bp.route("/reports/download_pdf")
@login_required
def download_pdf():
    allowed_event_ids = get_event_ids_for_current_user()
    category_id = request.args.get("category_id", type=int)

    part_q = db.session.query(Event.title, func.count(EventAttendance.user_id)).join(EventAttendance).filter(EventAttendance.status == "confirmed", Event.id.in_(allowed_event_ids))
    if category_id:
        part_q = part_q.filter(Event.category_id == category_id)
    participation_data = part_q.group_by(Event.id).all()

    feedback_q = db.session.query(Event.title, func.avg(EventFeedback.rating)).join(EventFeedback).filter(Event.id.in_(allowed_event_ids))
    if category_id:
        feedback_q = feedback_q.filter(Event.category_id == category_id)
    feedback_data = feedback_q.group_by(Event.id).all()

    analytics = Analytics()
    event_stats = analytics.get_event_stats()
    user_stats = analytics.get_user_stats()
    club_stats = analytics.get_club_stats()
    feedback_stats = analytics.get_feedback_stats()

    base64_participation_chart = generate_participation_chart(participation_data)
    base64_category_chart = generate_category_chart(event_stats["event_by_category"])
    base64_rating_chart = generate_rating_chart(feedback_stats["rating_distribution"])
    base64_club_chart = generate_club_chart(club_stats["most_active_clubs"])

    html = render_template(
        "report/pdf_template.html",
        participation_data=participation_data,
        feedback_data=feedback_data,
        event_stats=event_stats,
        user_stats=user_stats,
        club_stats=club_stats,
        feedback_stats=feedback_stats,
        current_date=datetime.utcnow(),
        base64_image=base64_participation_chart,
        base64_category_chart=base64_category_chart,
        base64_rating_chart=base64_rating_chart,
        base64_club_chart=base64_club_chart,
    )
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
        return send_file(filepath, as_attachment=True, download_name=filepath.split("/")[-1], mimetype="text/csv")
    flash("Failed to generate feedback CSV.", "danger")
    return redirect(url_for("report.reports"))


@report_bp.route("/reports/export_attendance_csv")
@login_required
def export_attendance_csv():
    allowed_event_ids = get_event_ids_for_current_user()
    filepath = export_event_attendance_to_csv(allowed_event_ids=allowed_event_ids)
    if filepath:
        flash("Attendance CSV generated successfully!", "success")
        return send_file(filepath, as_attachment=True, download_name=filepath.split("/")[-1], mimetype="text/csv")
    flash("Failed to generate attendance CSV.", "danger")
    return redirect(url_for("report.reports"))


@report_bp.route("/reports/export_stats_csv")
@login_required
def export_stats_csv():
    analytics = Analytics()
    event_stats = analytics.get_event_stats()
    user_stats = analytics.get_user_stats()
    club_stats = analytics.get_club_stats()

    event_filepath = export_event_stats_to_csv(event_stats)
    user_filepath = export_user_stats_to_csv(user_stats)
    club_filepath = export_club_stats_to_csv(club_stats)

    if event_filepath and user_filepath and club_filepath:
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.write(event_filepath, event_filepath.split("/")[-1])
            zip_file.write(user_filepath, user_filepath.split("/")[-1])
            zip_file.write(club_filepath, club_filepath.split("/")[-1])
        zip_buffer.seek(0)
        fname = f"all_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        return send_file(zip_buffer, as_attachment=True, download_name=fname, mimetype="application/zip")
    flash("Failed to generate statistics files.", "danger")
    return redirect(url_for("report.reports"))
