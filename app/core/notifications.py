from datetime import datetime
from app.core.extensions import db, mail
from app.models import Notification, User
from flask import url_for
from flask_mail import Message
from flask import current_app


def send_notification(user_id, message, notification_type="info"):
    notification = Notification(user_id=user_id, message=message, notification_type=notification_type)
    db.session.add(notification)
    db.session.commit()
