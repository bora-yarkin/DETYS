from flask_apscheduler import APScheduler
from app.models import Event, EventAttendance
from datetime import datetime, timedelta
from app.core.notifications import send_notification
from flask import current_app

scheduler = APScheduler()

@scheduler.task('interval', id='check_upcoming_events', hours=1)
def check_upcoming_events():
    """Her saatte bir yaklaşan etkinlikleri kontrol eder"""
    with scheduler.app.app_context():
        upcoming_events = Event.query.filter(
            Event.date > datetime.now(),
            Event.date <= datetime.now() + timedelta(hours=1)
        ).all()
        
        for event in upcoming_events:
            # Get confirmed attendees for the event
            attendees = EventAttendance.query.filter_by(
                event_id=event.id,
                status="confirmed"
            ).all()
            
            for attendance in attendees:
                message = f"Reminder: Event '{event.title}' starts in less than an hour!"
                send_notification(
                    user_id=attendance.user_id,
                    message=message,
                    notification_type="info"
                ) 