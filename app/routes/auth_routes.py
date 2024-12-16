from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms import RegistrationForm, LoginForm
from app.core.extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    login_form = LoginForm()
    registration_form = RegistrationForm()

    if request.method == "POST":
        action = request.form.get('action')
        if action == 'login' and login_form.validate_on_submit():
            # Username ile giriş yapılıyor
            user = User.query.filter_by(username=login_form.username.data).first()
            if user and user.check_password(login_form.password.data):
                login_user(user)
                flash("Başarıyla giriş yaptınız.", "success")
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("main.dashboard"))
            else:
                flash("Geçersiz kullanıcı adı veya şifre.", "danger")
        elif action == 'register' and registration_form.validate_on_submit():
            user = User(
                username=registration_form.username.data, 
                email=registration_form.email.data, 
                role=registration_form.role.data
            )
            user.set_password(registration_form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Kayıt başarılı! Şimdi giriş yapabilirsiniz.", "success")
            return redirect(url_for("auth.login"))
        else:
            # Form doğrulama hatalarını işleme
            for form in [login_form, registration_form]:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Hata: {getattr(form, field).label.text} - {error}", "danger")

    return render_template("auth/login.html", login_form=login_form, registration_form=registration_form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for("auth.login"))