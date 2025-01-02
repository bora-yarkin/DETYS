from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from app.forms import UserProfileForm
from app.core.extensions import db

# Profile blueprint'i oluşturur
profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


# Kullanıcı profilini yönetir
@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def manage_profile():
    # Kullanıcının mevcut bilgilerini form nesnesine aktarır
    form = UserProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Formdan gelen verilerle kullanıcı bilgilerini günceller
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        # Değişiklikleri veritabanına kaydeder
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.manage_profile"))
    # Profil yönetim formunu user/profile.html şablonuna gönderir
    return render_template("user/profile.html", form=form)


# Kullanıcı hesabını siler
@profile_bp.route("/delete", methods=["POST"])
@login_required
def delete_account():
    # Mevcut kullanıcı nesnesini alır
    user = current_user._get_current_object()
    # Kullanıcıyı oturumdan çıkarır
    logout_user()
    # Kullanıcıyı veritabanından siler
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted.", "success")
    # Ana sayfaya yönlendirir
    return redirect(url_for("main.home"))
