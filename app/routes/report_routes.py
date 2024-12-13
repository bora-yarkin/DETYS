from flask import Blueprint, render_template, send_file
from flask_login import login_required, current_user
from datetime import datetime
from io import BytesIO
import base64
import matplotlib
import matplotlib.pyplot as plt

from app.core.extensions import db
from app.models import Event, EventAttendance, EventFeedback
from app.core.decorators import main_admin_required
from xhtml2pdf import pisa

matplotlib.use("Agg")

report_bp = Blueprint("report", __name__)


@report_bp.route("/reports")
@login_required
@main_admin_required
def reports():
    participation_data = db.session.query(Event.title, db.func.count(EventAttendance.user_id)).join(EventAttendance, Event.id == EventAttendance.event_id).filter(EventAttendance.status == "confirmed").group_by(Event.id).all()

    sorted_by_popularity = sorted(participation_data, key=lambda x: x[1], reverse=True)[:5]

    feedback_data = db.session.query(Event.title, db.func.avg(EventFeedback.rating)).join(EventFeedback, Event.id == EventFeedback.event_id).group_by(Event.id).all()

    base64_image = None
    if participation_data:
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

        base64_image = "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    return render_template("report/report.html", participation_data=participation_data, sorted_by_popularity=sorted_by_popularity, feedback_data=feedback_data, base64_image=base64_image)


@report_bp.route("/reports/download_pdf")
@login_required
@main_admin_required
def download_pdf():
    participation_data = db.session.query(Event.title, db.func.count(EventAttendance.user_id)).join(EventAttendance, Event.id == EventAttendance.event_id).filter(EventAttendance.status == "confirmed").group_by(Event.id).all()

    feedback_data = db.session.query(Event.title, db.func.avg(EventFeedback.rating)).join(EventFeedback, Event.id == EventFeedback.event_id).group_by(Event.id).all()

    base64_image = None
    if participation_data:
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

        base64_image = "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    html = render_template("report/pdf_template.html", participation_data=participation_data, feedback_data=feedback_data, current_date=datetime.utcnow(), base64_image=base64_image)

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=pdf_buffer, encoding="utf-8")

    if pisa_status.err:
        return "Error generating PDF", 500

    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=True, download_name="report.pdf", mimetype="application/pdf")
