from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms import RegistrationForm, LoginForm
from app.core.extensions import db

# Auth blueprint'i oluşturur
auth_bp = Blueprint("auth", __name__)


# Kullanıcı giriş işlemi
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Kullanıcı zaten giriş yapmışsa dashboard'a yönlendirir
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    login_form = LoginForm()
    registration_form = RegistrationForm()

    if request.method == "POST":
        action = request.form.get("action")
        # Giriş işlemi
        if action == "login" and login_form.validate_on_submit():
            user = User.query.filter_by(username=login_form.username.data).first()
            if user and user.check_password(login_form.password.data):
                login_user(user)
                flash("Login Successful.", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("main.dashboard"))
            else:
                flash("Wrong username or password.", "danger")
        # Kayıt işlemi
        elif action == "register" and registration_form.validate_on_submit():
            user = User(username=registration_form.username.data, email=registration_form.email.data, role="student")
            user.set_password(registration_form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful, you can login now.", "success")
            return redirect(url_for("auth.login"))
        else:
            for field, errors in registration_form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(registration_form, field).label.text}: {error}", "danger")

    return render_template("auth/login.html", login_form=login_form, registration_form=registration_form)


# Kullanıcı çıkış işlemi
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout successful.", "info")
    return redirect(url_for("auth.login"))
