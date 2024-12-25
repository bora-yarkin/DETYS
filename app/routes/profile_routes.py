from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from app.forms import UserProfileForm
from app.core.extensions import db

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def manage_profile():
    form = UserProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.manage_profile"))
    return render_template("user/profile.html", form=form)


@profile_bp.route("/delete", methods=["POST"])
@login_required
def delete_account():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted.", "success")
    return redirect(url_for("main.home"))
