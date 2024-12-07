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


# TODO: Implement Mail based notifications

# def send_email_notification(user_id, subject, body):
#     user = User.query.get(user_id)
#     if not user:
#         return

#     msg = Message(subject=subject, sender=current_app.config["MAIL_DEFAULT_SENDER"], recipients=[user.email], body=body)
#     mail.send(msg)
