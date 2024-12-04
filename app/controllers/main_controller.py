from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.post import Post
from app.models.contact_message import ContactMessage
from app.utils.decorators import club_manager_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    posts = Post.query.order_by(Post.posted_at.desc()).all()
    return render_template("index.html", posts=posts)


@main_bp.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("view_post.html", post=post)


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Handle form submission
        name = request.form.get("name")
        email = request.form.get("email")
        message_text = request.form.get("message")

        # Save the message to the database
        message = ContactMessage(name=name, email=email, message=message_text)
        db.session.add(message)
        db.session.commit()

        flash("Your message has been sent!", "success")
        return redirect(url_for("main.contact"))

    return render_template("contact.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@main_bp.route("/club-manager-only")
@login_required
@club_manager_required
def club_manager_page():
    return "This page is only accessible to club managers."
