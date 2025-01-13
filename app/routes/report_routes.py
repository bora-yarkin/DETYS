import os
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile
from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app.core.extensions import db
from app.core.decorators import admin_or_manager_required
from app.core.analytics import Analytics
from app.models import Category, Event, EventAttendance, EventFeedback, Club, User
from app.core.data_processing import export_event_feedback_to_csv, export_event_attendance_to_csv, export_event_stats_to_csv, export_user_stats_to_csv, export_club_stats_to_csv
from app.core.visualizations import ChartGenerator
from xhtml2pdf import pisa

import matplotlib

matplotlib.use("Agg")

report_bp = Blueprint("report", __name__)


def get_allowed_event_ids():
    # Kullanıcının erişimine izin verilen etkinlik ID'lerini alır
    if current_user.is_main_admin:
        # Eğer kullanıcı ana yönetici ise tüm etkinliklerin ID'lerini döner
        return [event.id for event in Event.query.all()]
    # Kullanıcının yönettiği kulüpleri sorgular
    managed_clubs = Club.query.filter_by(president_id=current_user.id).all()
    club_ids = [club.id for club in managed_clubs]
    # Yönettiği kulüplere ait etkinliklerin ID'lerini döner
    return [event.id for event in Event.query.filter(Event.club_id.in_(club_ids)).all()]


@report_bp.route("/reports")
@login_required
@admin_or_manager_required
def reports():
    allowed_event_ids = get_allowed_event_ids()

    # Filtre parametrelerini okur ve datetime nesnelerine dönüştürür
    from_date_str = request.args.get("from_date")
    to_date_str = request.args.get("to_date")

    from_date_obj = None
    to_date_obj = None

    if from_date_str:
        try:
            from_date_obj = datetime.strptime(from_date_str, "%Y-%m-%d")
        except ValueError:
            pass

    if to_date_str:
        try:
            to_date_obj = datetime.strptime(to_date_str, "%Y-%m-%d")
        except ValueError:
            pass

    category_ids = request.args.getlist("category_ids", type=int)
    club_id = request.args.get("club_id", type=int)
    category_id = request.args.get("category_id", type=int)

    participation_query = (
        db.session.query(
            Event.title,
            func.count(EventAttendance.user_id).label("attendee_count"),
        )
        .join(EventAttendance)
        .filter(
            EventAttendance.status == "confirmed",
            Event.id.in_(allowed_event_ids),
        )
    )
    if from_date_obj:
        participation_query = participation_query.filter(Event.date >= from_date_obj)
    if to_date_obj:
        participation_query = participation_query.filter(Event.date <= to_date_obj)
    if category_ids:
        participation_query = participation_query.filter(Event.category_id.in_(category_ids))
    if club_id:
        participation_query = participation_query.filter(Event.club_id == club_id)

    participation_data = participation_query.group_by(Event.id, Event.title).all()

    popular_query = (
        db.session.query(
            Event.title,
            func.count(EventAttendance.user_id).label("cnt"),
        )
        .join(EventAttendance)
        .filter(
            EventAttendance.status == "confirmed",
            Event.id.in_(allowed_event_ids),
        )
    )
    if from_date_obj:
        popular_query = popular_query.filter(Event.date >= from_date_obj)
    if to_date_obj:
        popular_query = popular_query.filter(Event.date <= to_date_obj)
    if category_ids:
        popular_query = popular_query.filter(Event.category_id.in_(category_ids))
    if club_id:
        popular_query = popular_query.filter(Event.club_id == club_id)

    sorted_by_popularity = popular_query.group_by(Event.id, Event.title).order_by(func.count(EventAttendance.user_id).desc()).limit(5).all()

    analytics = Analytics()
    event_stats = analytics.get_event_stats()
    user_stats = analytics.get_user_stats()
    club_stats = analytics.get_club_stats()
    feedback_stats = analytics.get_feedback_stats()

    try:
        participation_chart = ChartGenerator.generate_bar_chart(
            labels=[item.title for item in participation_data],
            values=[item.attendee_count for item in participation_data],
            title="Event Participation",
            xlabel="Events",
            ylabel="Number of Participants",
            rotation=45,
        )
    except Exception as e:
        participation_chart = None
        flash(f"Error generating participation chart: {e}", "danger")

    try:
        category_labels = [cat[0] for cat in event_stats["event_by_category"]]
        category_values = [cat[1] for cat in event_stats["event_by_category"]]
        categories_chart = ChartGenerator.generate_pie_chart(
            labels=category_labels,
            sizes=category_values,
            title="Events by Category",
        )
    except Exception as e:
        categories_chart = None
        flash(f"Error generating categories chart: {e}", "danger")

    try:
        rating_labels = [str(r[0]) for r in feedback_stats["rating_distribution"]]
        rating_values = [r[1] for r in feedback_stats["rating_distribution"]]
        ratings_chart = ChartGenerator.generate_bar_chart(
            labels=rating_labels,
            values=rating_values,
            title="Rating Distribution",
            xlabel="Rating",
            ylabel="Count",
            rotation=0,
        )
    except Exception as e:
        ratings_chart = None
        flash(f"Error generating ratings chart: {e}", "danger")

    try:
        club_labels = [c[0] for c in club_stats["most_active_clubs"]]
        club_values = [c[1] for c in club_stats["most_active_clubs"]]
        clubs_chart = ChartGenerator.generate_bar_chart(
            labels=club_labels,
            values=club_values,
            title="Most Active Clubs",
            xlabel="Clubs",
            ylabel="Number of Events",
            rotation=45,
        )
    except Exception as e:
        clubs_chart = None
        flash(f"Error generating clubs chart: {e}", "danger")

    try:
        user_engagement_query = (
            db.session.query(
                User.username,
                func.count(EventAttendance.event_id).label("events_attended"),
            )
            .join(EventAttendance)
            .join(Event)
            .filter(
                EventAttendance.status == "confirmed",
                Event.id.in_(allowed_event_ids),
            )
        )
        if from_date_obj:
            user_engagement_query = user_engagement_query.filter(Event.date >= from_date_obj)
        if to_date_obj:
            user_engagement_query = user_engagement_query.filter(Event.date <= to_date_obj)
        if category_ids:
            user_engagement_query = user_engagement_query.filter(Event.category_id.in_(category_ids))
        if club_id:
            user_engagement_query = user_engagement_query.filter(Event.club_id == club_id)

        scatter_x, scatter_y = [], []
        for user_data in user_engagement_query.group_by(User.username).all():
            scatter_x.append(user_data.username)
            scatter_y.append(user_data.events_attended)

        user_engagement_chart = ChartGenerator.generate_scatter_plot(
            x=scatter_x,
            y=scatter_y,
            title="User Engagement",
            xlabel="User",
            ylabel="Number of Events Attended",
        )
    except Exception as e:
        user_engagement_chart = None
        flash(f"Error generating user engagement chart: {e}", "danger")

    try:
        feedback_query = EventFeedback.query.join(Event).filter(Event.id.in_(allowed_event_ids))
        if from_date_obj:
            feedback_query = feedback_query.filter(Event.date >= from_date_obj)
        if to_date_obj:
            feedback_query = feedback_query.filter(Event.date <= to_date_obj)
        if category_ids:
            feedback_query = feedback_query.filter(Event.category_id.in_(category_ids))
        if club_id:
            feedback_query = feedback_query.filter(Event.club_id == club_id)

        feedback_ratings = [fb.rating for fb in feedback_query.all()]
        feedback_histogram = ChartGenerator.generate_histogram(
            data=feedback_ratings,
            bins=5,
            title="Histogram of Feedback Ratings",
            xlabel="Rating",
            ylabel="Frequency",
        )
    except Exception as e:
        feedback_histogram = None
        flash(f"Error generating feedback histogram: {e}", "danger")

    base64_charts = {
        "participation": participation_chart,
        "categories": categories_chart,
        "ratings": ratings_chart,
        "club_activity": clubs_chart,
        "user_engagement": user_engagement_chart,
        "feedback_histogram": feedback_histogram,
    }

    feedback_data_query = (
        db.session.query(
            Event.title,
            func.avg(EventFeedback.rating).label("avg_rating"),
        )
        .join(EventFeedback)
        .filter(Event.id.in_(allowed_event_ids))
    )
    if from_date_obj:
        feedback_data_query = feedback_data_query.filter(Event.date >= from_date_obj)
    if to_date_obj:
        feedback_data_query = feedback_data_query.filter(Event.date <= to_date_obj)
    if category_ids:
        feedback_data_query = feedback_data_query.filter(Event.category_id.in_(category_ids))
    if club_id:
        feedback_data_query = feedback_data_query.filter(Event.club_id == club_id)

    feedback_data = feedback_data_query.group_by(Event.id).all()

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
        from_date=from_date_str,
        to_date=to_date_str,
        selected_categories=category_ids,
        selected_club=club_id,
        clubs=Club.query.order_by(Club.name.asc()).all(),
    )


@report_bp.route("/reports/download_pdf")
@login_required
@admin_or_manager_required
def download_pdf():
    # Kullanıcının erişimine izin verilen etkinlik ID'lerini alır
    allowed_event_ids = get_allowed_event_ids()
    # Kategori filtresini alır
    category_id = request.args.get("category_id", type=int)

    # Etkinlik katılım verilerini sorgular
    part_q = (
        db.session.query(
            Event.title,
            func.count(EventAttendance.user_id).label("attendee_count"),
        )
        .join(EventAttendance)
        .filter(
            EventAttendance.status == "confirmed",
            Event.id.in_(allowed_event_ids),
        )
    )
    if category_id:
        part_q = part_q.filter(Event.category_id == category_id)
    participation_data = part_q.group_by(Event.id, Event.title).all()

    # Geri bildirim verilerini sorgular
    feedback_q = (
        db.session.query(
            Event.title,
            func.avg(EventFeedback.rating).label("avg_rating"),
        )
        .join(EventFeedback)
        .filter(Event.id.in_(allowed_event_ids))
    )
    if category_id:
        feedback_q = feedback_q.filter(Event.category_id == category_id)
    feedback_data = feedback_q.group_by(Event.id).all()

    # Analiz istatistiklerini alır
    analytics = Analytics()
    event_stats = analytics.get_event_stats()
    user_stats = analytics.get_user_stats()
    club_stats = analytics.get_club_stats()
    feedback_stats = analytics.get_feedback_stats()

    # Etkinlik katılım grafiğini PDF için oluşturur
    try:
        participation_chart = ChartGenerator.generate_bar_chart(
            labels=[item.title for item in participation_data],
            values=[item.attendee_count for item in participation_data],
            title="Event Participation",
            xlabel="Events",
            ylabel="Number of Participants",
            rotation=45,
        )
    except Exception as e:
        participation_chart = None
        flash(f"Error generating participation chart for PDF: {e}", "danger")

    # Kategorilere göre etkinlik dağılım grafiğini PDF için oluşturur
    try:
        category_labels = [category[0] for category in event_stats["event_by_category"]]
        category_values = [category[1] for category in event_stats["event_by_category"]]
        categories_chart = ChartGenerator.generate_pie_chart(
            labels=category_labels,
            sizes=category_values,
            title="Events by Category",
        )
    except Exception as e:
        categories_chart = None
        flash(f"Error generating categories chart for PDF: {e}", "danger")

    # Geri bildirim puan dağılım grafiğini PDF için oluşturur
    try:
        rating_labels = [str(rating[0]) for rating in feedback_stats["rating_distribution"]]
        rating_values = [rating[1] for rating in feedback_stats["rating_distribution"]]
        ratings_chart = ChartGenerator.generate_bar_chart(
            labels=rating_labels,
            values=rating_values,
            title="Rating Distribution",
            xlabel="Rating",
            ylabel="Count",
            rotation=0,
        )
    except Exception as e:
        ratings_chart = None
        flash(f"Error generating ratings chart for PDF: {e}", "danger")

    # En aktif kulüpler grafiğini PDF için oluşturur
    try:
        club_labels = [club[0] for club in club_stats["most_active_clubs"]]
        club_values = [club[1] for club in club_stats["most_active_clubs"]]
        clubs_chart = ChartGenerator.generate_bar_chart(
            labels=club_labels,
            values=club_values,
            title="Most Active Clubs",
            xlabel="Clubs",
            ylabel="Number of Events",
            rotation=45,
        )
    except Exception as e:
        clubs_chart = None
        flash(f"Error generating clubs chart for PDF: {e}", "danger")

    # Kullanıcı etkileşim grafiğini PDF için oluşturur
    try:
        user_engagement_query = (
            db.session.query(
                User.username,
                func.count(EventAttendance.event_id).label("events_attended"),
            )
            .join(EventAttendance)
            .group_by(User.username)
            .all()
        )

        scatter_x = [user.username for user in user_engagement_query]
        scatter_y = [user.events_attended for user in user_engagement_query]
        user_engagement_chart = ChartGenerator.generate_scatter_plot(
            x=scatter_x,
            y=scatter_y,
            title="User Engagement",
            xlabel="User",
            ylabel="Number of Events Attended",
        )
    except Exception as e:
        user_engagement_chart = None
        flash(f"Error generating user engagement chart for PDF: {e}", "danger")

    # Geri bildirim puan histogramını PDF için oluşturur
    try:
        feedback_ratings = [fb.rating for fb in EventFeedback.query.all()]
        feedback_histogram = ChartGenerator.generate_histogram(
            data=feedback_ratings,
            bins=5,
            title="Histogram of Feedback Ratings",
            xlabel="Rating",
            ylabel="Frequency",
        )
    except Exception as e:
        feedback_histogram = None
        flash(f"Error generating feedback histogram for PDF: {e}", "danger")

    # Oluşturulan tüm grafikleri Base64 formatında sözlüğe ekler
    base64_participation_chart = participation_chart
    base64_category_chart = categories_chart
    base64_rating_chart = ratings_chart
    base64_club_chart = clubs_chart
    base64_user_engagement_chart = user_engagement_chart
    base64_feedback_histogram = feedback_histogram

    # PDF formatına dönüştürülecek HTML içeriğini render eder
    html = render_template(
        "report/pdf_template.html",
        participation_data=participation_data,
        feedback_data=feedback_data,
        event_stats=event_stats,
        user_stats=user_stats,
        club_stats=club_stats,
        feedback_stats=feedback_stats,
        current_date=datetime.utcnow(),
        base64_participation_chart=base64_participation_chart,
        base64_category_chart=base64_category_chart,
        base64_rating_chart=base64_rating_chart,
        base64_club_chart=base64_club_chart,
        base64_user_engagement_chart=base64_user_engagement_chart,
        base64_feedback_histogram=base64_feedback_histogram,
    )

    # PDF oluşturmak için BytesIO buffer'ını başlatır
    pdf_buffer = BytesIO()
    # HTML içeriğini PDF'e dönüştürür
    pisa_status = pisa.CreatePDF(src=html, dest=pdf_buffer, encoding="utf-8")
    if pisa_status.err:
        # PDF oluşturma başarısız olursa hata mesajı gösterir
        flash("Error generating PDF report.", "danger")
        return redirect(url_for("report.reports"))
    # Buffer'ı başa çevirir
    pdf_buffer.seek(0)
    # Oluşturulan PDF dosyasını indirme olarak kullanıcıya gönderir
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="report.pdf",
        mimetype="application/pdf",
    )


@report_bp.route("/reports/export_feedback_csv")
@login_required
@admin_or_manager_required
def export_feedback_csv():
    # Kullanıcının erişimine izin verilen etkinlik ID'lerini alır
    allowed_event_ids = get_allowed_event_ids()
    # Kategori filtresini alır
    category_id = request.args.get("category_id", type=int)

    try:
        # Geri bildirim verilerini CSV'e aktarır
        filepath = export_event_feedback_to_csv(allowed_event_ids=allowed_event_ids, category_id=category_id)
        if filepath and os.path.exists(filepath):
            # CSV dosyasının başarıyla oluşturulduğunu bildirir
            flash("Feedback CSV generated successfully!", "success")
            # CSV dosyasını indirme olarak kullanıcıya gönderir
            return send_file(
                filepath,
                as_attachment=True,
                download_name=os.path.basename(filepath),
                mimetype="text/csv",
            )
        else:
            # CSV oluşturma başarısız olursa hata mesajı gösterir
            flash("Failed to generate feedback CSV.", "danger")
            return redirect(url_for("report.reports"))
    except Exception as e:
        # CSV aktarımı sırasında oluşan hataları yakalar ve bildirir
        flash(f"An error occurred while exporting Feedback CSV: {e}", "danger")
        return redirect(url_for("report.reports"))


@report_bp.route("/reports/export_attendance_csv")
@login_required
@admin_or_manager_required
def export_attendance_csv():
    # Kullanıcının erişimine izin verilen etkinlik ID'lerini alır
    allowed_event_ids = get_allowed_event_ids()
    # Kategori filtresini alır
    category_id = request.args.get("category_id", type=int)

    try:
        # Katılım verilerini CSV'e aktarır
        filepath = export_event_attendance_to_csv(allowed_event_ids=allowed_event_ids, category_id=category_id)
        if filepath and os.path.exists(filepath):
            # CSV dosyasının başarıyla oluşturulduğunu bildirir
            flash("Attendance CSV generated successfully!", "success")
            # CSV dosyasını indirme olarak kullanıcıya gönderir
            return send_file(
                filepath,
                as_attachment=True,
                download_name=os.path.basename(filepath),
                mimetype="text/csv",
            )
        else:
            # CSV oluşturma başarısız olursa hata mesajı gösterir
            flash("Failed to generate attendance CSV.", "danger")
            return redirect(url_for("report.reports"))
    except Exception as e:
        # CSV aktarımı sırasında oluşan hataları yakalar ve bildirir
        flash(f"An error occurred while exporting Attendance CSV: {e}", "danger")
        return redirect(url_for("report.reports"))


@report_bp.route("/reports/export_stats_csv")
@login_required
@admin_or_manager_required
def export_stats_csv():
    try:
        # Analiz istatistiklerini alır
        analytics = Analytics()
        event_stats = analytics.get_event_stats()
        user_stats = analytics.get_user_stats()
        club_stats = analytics.get_club_stats()

        # İstatistik verilerini CSV'e aktarır
        event_filepath = export_event_stats_to_csv(event_stats)
        user_filepath = export_user_stats_to_csv(user_stats)
        club_filepath = export_club_stats_to_csv(club_stats)

        if event_filepath and user_filepath and club_filepath:
            # ZIP dosyası oluşturmak için BytesIO buffer'ını başlatır
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w") as zip_file:
                # Her CSV dosyasını ZIP arşivine ekler
                zip_file.write(event_filepath, os.path.basename(event_filepath))
                zip_file.write(user_filepath, os.path.basename(user_filepath))
                zip_file.write(club_filepath, os.path.basename(club_filepath))
            # Buffer'ı başa çevirir
            zip_buffer.seek(0)
            # Eşsiz bir dosya adı oluşturur
            fname = f"all_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            # ZIP dosyasını indirme olarak kullanıcıya gönderir
            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name=fname,
                mimetype="application/zip",
            )
        else:
            # CSV dosyalarını oluşturma başarısız olursa hata mesajı gösterir
            flash("Failed to generate statistics files.", "danger")
            return redirect(url_for("report.reports"))
    except Exception as e:
        # ZIP oluşturma sırasında oluşan hataları yakalar ve bildirir
        flash(f"An error occurred while exporting Statistics ZIP: {e}", "danger")
        return redirect(url_for("report.reports"))
