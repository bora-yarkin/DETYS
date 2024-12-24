from functools import wraps
from flask import abort
from flask_login import current_user
from app.models import Membership, Club


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


student_required = roles_required("student")
club_manager_required = roles_required("club_manager")
main_admin_required = roles_required("main_admin")
admin_or_manager_required = roles_required("main_admin", "club_manager")


def club_member_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        club_id = kwargs.get("club_id")
        if not current_user.is_authenticated:
            abort(403)
        membership = Membership.query.filter_by(user_id=current_user.id, club_id=club_id, is_approved=True).first()
        if not membership:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def club_member_or_manager_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        club_id = kwargs.get("club_id")
        if not current_user.is_authenticated:
            abort(403)
        if current_user.is_main_admin:
            return f(*args, **kwargs)
        club = Club.query.get_or_404(club_id)
        if club.president_id == current_user.id:
            return f(*args, **kwargs)
        membership = Membership.query.filter_by(user_id=current_user.id, club_id=club_id, is_approved=True).first()

        if not membership:
            abort(403)

        return f(*args, **kwargs)

    return wrapper
