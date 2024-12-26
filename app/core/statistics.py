from sqlalchemy import func, distinct, extract
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

from app.models import EventAttendance, EventFeedback, User, Club, Membership, Event, Category
from app.core.extensions import db


def get_rating_distribution():
    """Get distribution of event ratings"""
    ratings = db.session.query(EventFeedback.rating, func.count(EventFeedback.id)).group_by(EventFeedback.rating).all()
    return {"labels": [str(r[0]) for r in ratings], "data": [r[1] for r in ratings]}


def get_active_users_count():
    """Count users active in the last 30 days"""
    thirty_days_ago = datetime.now() - timedelta(days=30)
    return db.session.query(func.count(distinct(EventAttendance.user_id))).filter(EventAttendance.registered_at >= thirty_days_ago).scalar()


def get_user_registration_trends():
    """Get user registration trends by month"""
    registrations = db.session.query(func.date_trunc("month", User.created_at), func.count(User.id)).group_by(func.date_trunc("month", User.created_at)).order_by(func.date_trunc("month", User.created_at)).all()
    return {"labels": [r[0].strftime("%Y-%m") for r in registrations], "data": [r[1] for r in registrations]}


def get_club_member_distribution():
    """Get distribution of members across clubs"""
    distribution = db.session.query(Club.name, func.count(Membership.user_id)).join(Membership).group_by(Club.name).all()
    return {"labels": [d[0] for d in distribution], "data": [d[1] for d in distribution]}


def calculate_club_activity_levels():
    """Calculate activity levels for each club"""
    thirty_days_ago = datetime.now() - timedelta(days=30)
    activities = db.session.query(Club.name, func.count(Event.id)).join(Event).filter(Event.date >= thirty_days_ago).group_by(Club.name).all()
    return {"labels": [a[0] for a in activities], "data": [a[1] for a in activities]}


def calculate_club_growth_rates():
    """Calculate month-over-month growth rates for clubs"""
    current_month = datetime.now().replace(day=1)
    last_month = current_month - timedelta(days=1)

    current_members = db.session.query(Club.name, func.count(Membership.user_id)).join(Membership).filter(Membership.joined_at < current_month).group_by(Club.name).all()

    last_month_members = db.session.query(Club.name, func.count(Membership.user_id)).join(Membership).filter(Membership.joined_at < last_month).group_by(Club.name).all()

    growth_rates = {}
    for club, current_count in current_members:
        last_count = next((count for c, count in last_month_members if c == club), 0)
        if last_count > 0:
            growth_rate = ((current_count - last_count) / last_count) * 100
        else:
            growth_rate = 100
        growth_rates[club] = growth_rate

    return {"labels": list(growth_rates.keys()), "data": list(growth_rates.values())}


def get_feedback_trends():
    """Get feedback trends over time"""
    feedback_trends = db.session.query(func.date_trunc("month", EventFeedback.submitted_at), func.avg(EventFeedback.rating)).group_by(func.date_trunc("month", EventFeedback.submitted_at)).order_by(func.date_trunc("month", EventFeedback.submitted_at)).all()

    return {"labels": [t[0].strftime("%Y-%m") for t in feedback_trends], "data": [float(t[1]) if t[1] else 0 for t in feedback_trends]}


def get_category_ratings():
    """Get average ratings by category"""
    category_ratings = db.session.query(Category.name, func.avg(EventFeedback.rating)).join(Event, Event.category_id == Category.id).join(EventFeedback, EventFeedback.event_id == Event.id).group_by(Category.name).all()

    return {"labels": [r[0] for r in category_ratings], "data": [float(r[1]) if r[1] else 0 for r in category_ratings]}
