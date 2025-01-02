from flask_apscheduler import APScheduler
from app.models import Event, EventAttendance
from datetime import datetime, timedelta
from app.core.notifications import send_notification
from app.core.extensions import db

scheduler = APScheduler()

@scheduler.task('interval', id='check_upcoming_events', minutes=1)
def check_upcoming_events():
    """Her dakikada bir yaklaşan etkinlikleri kontrol eder"""
    with scheduler.app.app_context():
        now = datetime.now()
        upcoming_events = Event.query.filter(
            Event.date > now,
            Event.date <= now + timedelta(hours=1),
            Event.date >= now + timedelta(minutes=59)
        ).all()
        
        for event in upcoming_events:
            attendees = EventAttendance.query.filter_by(
                event_id=event.id,
                status="confirmed"
            ).all()
            
            for attendance in attendees:
                time_until = int((event.date - now).total_seconds() / 60)
                message = f"Reminder: Event '{event.title}' starts in {time_until} minutes!"
                send_notification(
                    user_id=attendance.user_id,
                    message=message,
                    notification_type="info"
                ) 