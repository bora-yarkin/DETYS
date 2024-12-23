from functools import wraps
from flask import abort
from flask_login import current_user


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
