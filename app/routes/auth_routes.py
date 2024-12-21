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
        action = request.form.get("action")
        print(f"Form action: {action}")
        if action == "login" and login_form.validate_on_submit():
            user = User.query.filter_by(username=login_form.username.data).first()
            if user and user.check_password(login_form.password.data):
                login_user(user)
                flash("Başarıyla giriş yaptınız.", "success")
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("main.dashboard"))
            else:
                flash("Geçersiz kullanıcı adı veya şifre.", "danger")
        elif action == "register" and registration_form.validate_on_submit():
            print("Registration form validated")
            user = User(username=registration_form.username.data, email=registration_form.email.data, role=registration_form.role.data)
            user.set_password(registration_form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Kayıt başarılı! Şimdi giriş yapabilirsiniz.", "success")
            return redirect(url_for("auth.login"))
        else:
            print("Form validation failed")
            for field, errors in registration_form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    flash(f"Hata: {getattr(registration_form, field).label.text} - {error}", "danger")

    return render_template("auth/login.html", login_form=login_form, registration_form=registration_form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for("auth.login"))
