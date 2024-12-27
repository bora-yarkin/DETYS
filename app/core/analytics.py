from datetime import datetime, timedelta
from sqlalchemy import func, distinct
from app.core.extensions import db
from app.models import Event, EventAttendance, EventFeedback, User, Club, Category, Membership


class Analytics:
    @staticmethod
    def get_event_stats():
        attendance_subquery = db.session.query(EventAttendance.event_id, func.count(EventAttendance.user_id).label("attendee_count")).group_by(EventAttendance.event_id).subquery()

        average_attendance = db.session.query(func.avg(attendance_subquery.c.attendee_count)).scalar() or 0

        capacity_utilization = db.session.query(func.avg(Event.capacity * 1.0 / func.coalesce(attendance_subquery.c.attendee_count, 1))).scalar() or 0

        return {
            "total_events": Event.query.count(),
            "event_by_category": db.session.query(Category.name, func.count(Event.id)).join(Event).group_by(Category.name).all(),
            "average_attendance": float(average_attendance),
            "popular_days": db.session.query(func.extract("dow", Event.date), func.count(Event.id)).group_by(func.extract("dow", Event.date)).all(),
            "capacity_utilization": float(capacity_utilization),
        }

    @staticmethod
    def get_user_stats():
        thirty_days = datetime.utcnow() - timedelta(days=30)

        events_per_user = db.session.query(EventAttendance.user_id, func.count(EventAttendance.event_id).label("event_count")).group_by(EventAttendance.user_id).subquery()

        avg_events = db.session.query(func.avg(events_per_user.c.event_count)).scalar() or 0

        return {
            "total_users": User.query.count(),
            "active_users": db.session.query(func.count(distinct(EventAttendance.user_id))).filter(EventAttendance.registered_at >= thirty_days).scalar() or 0,
            "new_users": User.query.filter(User.created_at >= thirty_days).count(),
            "average_events_per_user": float(avg_events),
            "total_memberships": Membership.query.count(),  # New Statistic
        }

    @staticmethod
    def get_club_stats():
        members_subquery = db.session.query(Membership.club_id, func.count(Membership.user_id).label("member_count")).group_by(Membership.club_id).subquery()

        average_members = db.session.query(func.avg(members_subquery.c.member_count)).scalar() or 0

        return {
            "total_clubs": Club.query.count(),
            "avg_members": float(average_members),
            "most_active_clubs": db.session.query(Club.name, func.count(Event.id).label("event_count")).join(Event).group_by(Club.name).order_by(func.count(Event.id).desc()).limit(5).all(),
        }

    @staticmethod
    def get_feedback_stats():
        feedback_count_subquery = db.session.query(EventFeedback.event_id, func.count(EventFeedback.id).label("feedback_count")).group_by(EventFeedback.event_id).subquery()

        average_feedback_volume = db.session.query(func.avg(feedback_count_subquery.c.feedback_count)).scalar() or 0

        return {
            "avg_rating": db.session.query(func.avg(EventFeedback.rating)).scalar() or 0,
            "rating_distribution": db.session.query(EventFeedback.rating, func.count(EventFeedback.event_id)).group_by(EventFeedback.rating).all(),
            "top_rated_events": db.session.query(Event.title, func.avg(EventFeedback.rating).label("avg_rating")).join(EventFeedback).group_by(Event.title).order_by(func.avg(EventFeedback.rating).desc()).limit(5).all(),
            "average_feedback_volume": float(average_feedback_volume),  # New Statistic
        }
