from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from app.models import EventAttendance, EventFeedback, User, Club, Membership, Event, Category
from app.core.extensions import db


# Etkinlik geri bildirimlerinin puan dağılımını alır
def get_rating_distribution():
    # Her bir puan için kaç tane geri bildirim olduğunu sorgular
    ratings = db.session.query(EventFeedback.rating, func.count(EventFeedback.id)).group_by(EventFeedback.rating).all()
    # Puanları ve her puanın sayısını döner
    return {"labels": [str(r[0]) for r in ratings], "data": [r[1] for r in ratings]}


# Son 30 gün içinde aktif olan kullanıcı sayısını alır
def get_active_users_count():
    # 30 gün öncesinin tarihini hesaplar
    thirty_days_ago = datetime.now() - timedelta(days=30)
    # Son 30 gün içinde etkinliklere katılan benzersiz kullanıcıların sayısını sorgular
    return db.session.query(func.count(distinct(EventAttendance.user_id))).filter(EventAttendance.registered_at >= thirty_days_ago).scalar()


# Kullanıcı kayıt trendlerini alır
def get_user_registration_trends():
    # Kullanıcı kayıtlarını aylık olarak gruplar ve her ay için kaç kayıt olduğunu sorgular
    registrations = db.session.query(func.date_trunc("month", User.created_at), func.count(User.id)).group_by(func.date_trunc("month", User.created_at)).order_by(func.date_trunc("month", User.created_at)).all()
    # Ayları ve her ayın kayıt sayısını döner
    return {"labels": [r[0].strftime("%Y-%m") for r in registrations], "data": [r[1] for r in registrations]}


# Kulüp üye dağılımını alır
def get_club_member_distribution():
    # Her kulüp için üye sayısını sorgular
    distribution = db.session.query(Club.name, func.count(Membership.user_id)).join(Membership).group_by(Club.name).all()
    # Kulüp isimlerini ve her kulübün üye sayısını döner
    return {"labels": [d[0] for d in distribution], "data": [d[1] for d in distribution]}


# Kulüp etkinlik seviyelerini hesaplar
def calculate_club_activity_levels():
    # 30 gün öncesinin tarihini hesaplar
    thirty_days_ago = datetime.now() - timedelta(days=30)
    # Son 30 gün içinde her kulüp tarafından düzenlenen etkinliklerin sayısını sorgular
    activities = db.session.query(Club.name, func.count(Event.id)).join(Event).filter(Event.date >= thirty_days_ago).group_by(Club.name).all()
    # Kulüp isimlerini ve her kulübün etkinlik sayısını döner
    return {"labels": [a[0] for a in activities], "data": [a[1] for a in activities]}


# Kulüp büyüme oranlarını hesaplar
def calculate_club_growth_rates():
    # Geçerli ayın ilk gününü hesaplar
    current_month = datetime.now().replace(day=1)
    # Bir önceki ayın son gününü hesaplar
    last_month = current_month - timedelta(days=1)

    # Geçerli ayın başından önceki üye sayısını sorgular
    current_members = db.session.query(Club.name, func.count(Membership.user_id)).join(Membership).filter(Membership.joined_at < current_month).group_by(Club.name).all()

    # Bir önceki ayın başından önceki üye sayısını sorgular
    last_month_members = db.session.query(Club.name, func.count(Membership.user_id)).join(Membership).filter(Membership.joined_at < last_month).group_by(Club.name).all()

    growth_rates = {}
    # Her kulüp için büyüme oranını hesaplar
    for club, current_count in current_members:
        last_count = next((count for c, count in last_month_members if c == club), 0)
        if last_count > 0:
            growth_rate = ((current_count - last_count) / last_count) * 100
        else:
            growth_rate = 100
        growth_rates[club] = growth_rate

    # Kulüp isimlerini ve büyüme oranlarını döner
    return {"labels": list(growth_rates.keys()), "data": list(growth_rates.values())}


# Geri bildirim trendlerini alır
def get_feedback_trends():
    # Geri bildirimleri aylık olarak gruplar ve her ay için ortalama puanı sorgular
    feedback_trends = db.session.query(func.date_trunc("month", EventFeedback.submitted_at), func.avg(EventFeedback.rating)).group_by(func.date_trunc("month", EventFeedback.submitted_at)).order_by(func.date_trunc("month", EventFeedback.submitted_at)).all()

    # Ayları ve her ayın ortalama puanını döner
    return {"labels": [t[0].strftime("%Y-%m") for t in feedback_trends], "data": [float(t[1]) if t[1] else 0 for t in feedback_trends]}


# Kategori bazında puan ortalamalarını alır
def get_category_ratings():
    # Her kategori için ortalama puanı sorgular
    category_ratings = db.session.query(Category.name, func.avg(EventFeedback.rating)).join(Event, Event.category_id == Category.id).join(EventFeedback, EventFeedback.event_id == Event.id).group_by(Category.name).all()

    # Kategori isimlerini ve her kategorinin ortalama puanını döner
    return {"labels": [r[0] for r in category_ratings], "data": [float(r[1]) if r[1] else 0 for r in category_ratings]}
