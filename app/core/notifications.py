from datetime import datetime, timedelta
from app.core.extensions import db, mail
from app.models import Notification, User
from flask import url_for
from flask_mail import Message
from flask import current_app


def send_notification(user_id, message, notification_type="info"):
    notification = Notification(user_id=user_id, message=message, notification_type=notification_type)
    db.session.add(notification)
    db.session.commit()

def send_event_reminder_notification(event, user_id):
    """Etkinlikten bir saat önce hatırlatma bildirimi gönderir"""
    event_time = event.start_time  # event.start_time, etkinliğin başlama zamanını temsil eder
    current_time = datetime.now()
    time_difference = event_time - current_time

    # Etkinliğe bir saat veya daha az kaldıysa bildirim gönder
    if timedelta(hours=0) <= time_difference <= timedelta(hours=1):
        message = f"'{event.title}' etkinliği bir saat içinde başlayacak!"
        send_notification(user_id, message, notification_type="reminder")
