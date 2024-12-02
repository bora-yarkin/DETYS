from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def student_required(f):
    return role_required("student")(f)


def club_manager_required(f):
    return role_required("club_manager")(f)


def main_admin_required(f):
    return role_required("main_admin")(f)
