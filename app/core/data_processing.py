# Bu modül sistemdeki verilerin CSV formatında dışa aktarılmasını sağlar
# Etkinlik, kullanıcı ve kulüp verilerini raporlamak için kullanılır
import os
import csv
from datetime import datetime
from flask import current_app
from app.models import Event, EventFeedback, EventAttendance, User, Club
from app.core.extensions import db


def ensure_export_folder():
    # Export klasörünün varlığını kontrol et, yoksa oluştur
    export_folder = current_app.config.get("EXPORT_FOLDER")
    if not os.path.exists(export_folder):
        os.makedirs(export_folder, exist_ok=True)
    return export_folder


def export_query_to_csv(filename_prefix, headers, query, row_formatter):
    # Veritabanı sorgusu sonuçlarını CSV'ye aktaran genel fonksiyon
    export_folder = ensure_export_folder()
    filename = f"{filename_prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_folder, filename)

    data = query.all()

    # CSV dosyasını oluştur ve verileri yaz
    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row_formatter(row))

    return filepath


def export_list_to_csv(filename_prefix, headers, data):
    # Liste halindeki verileri CSV'ye aktaran yardımcı fonksiyon
    export_folder = ensure_export_folder()
    filename = f"{filename_prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_folder, filename)

    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

    return filepath


def export_event_feedback_to_csv(allowed_event_ids=None):
    # Etkinlik geri bildirimlerini dışa aktar
    # Etkinlik, kullanıcı ve geri bildirim tablolarını birleştir
    query = db.session.query(EventFeedback, Event.title, User.username).join(Event, EventFeedback.event_id == Event.id).join(User, EventFeedback.user_id == User.id)
    if allowed_event_ids is not None:
        query = query.filter(Event.id.in_(allowed_event_ids))

    headers = ["Event Title", "Username", "Rating", "Comment", "Submitted At"]

    def row_formatter(row):
        feedback_obj = row[0]
        event_title = row[1]
        username = row[2]
        return [
            event_title,
            username,
            feedback_obj.rating,
            feedback_obj.comment if feedback_obj.comment else "",
            feedback_obj.submitted_at.isoformat() if feedback_obj.submitted_at else "",
        ]

    return export_query_to_csv("event_feedback", headers, query, row_formatter)


def export_event_attendance_to_csv(allowed_event_ids=None):
    # Etkinlik katılım bilgilerini dışa aktar
    # Etkinlik, kulüp ve kullanıcı bilgilerini birleştir
    query = db.session.query(EventAttendance, Event.title, User.username, Club.name).join(Event, EventAttendance.event_id == Event.id).join(User, EventAttendance.user_id == User.id).join(Club, Event.club_id == Club.id)
    if allowed_event_ids is not None:
        query = query.filter(Event.id.in_(allowed_event_ids))

    headers = ["Event Title", "Club Name", "Username", "Status", "Registered At"]

    def row_formatter(row):
        attendance_obj = row[0]
        event_title = row[1]
        username = row[2]
        club_name = row[3]
        return [
            event_title,
            club_name,
            username,
            attendance_obj.status,
            attendance_obj.registered_at.isoformat() if attendance_obj.registered_at else "",
        ]

    return export_query_to_csv("event_attendance", headers, query, row_formatter)


def export_event_stats_to_csv(event_stats):
    # Etkinlik istatistiklerini CSV'ye aktar
    headers = ["Metric", "Value"]
    rows = []
    rows.append(["Total Events", event_stats["total_events"]])
    rows.append(["Average Attendance", f"{event_stats['average_attendance']:.2f}"])

    # Kategorilere göre etkinlik dağılımını ekle
    for cat_name, count in event_stats["event_by_category"]:
        rows.append([f"Category: {cat_name}", count])

    return export_list_to_csv("event_stats", headers, rows)


def export_user_stats_to_csv(user_stats):
    # Kullanıcı istatistiklerini CSV'ye aktar
    headers = ["Metric", "Value"]
    rows = [
        ["Total Users", user_stats["total_users"]],
        ["Active Users (30 days)", user_stats["active_users"]],
        ["New Users (30 days)", user_stats["new_users"]],
        ["Average Events per User", f"{user_stats['average_events_per_user']:.2f}"],
    ]
    return export_list_to_csv("user_stats", headers, rows)


def export_club_stats_to_csv(club_stats):
    # Kulüp istatistiklerini CSV'ye aktar
    headers = ["Metric", "Value"]
    rows = []
    rows.append(["Total Clubs", club_stats["total_clubs"]])
    rows.append(["Average Members per Club", f"{club_stats['avg_members']:.2f}"])

    # En aktif kulüpleri ekle
    for club, count in club_stats["most_active_clubs"]:
        rows.append([f"Most Active: {club}", count])

    return export_list_to_csv("club_stats", headers, rows)
