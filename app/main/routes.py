from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Post, ContactMessage
from app.forms import PostForm, ContactForm
from app.extensions import db
from . import main_bp


@main_bp.app_errorhandler(403)
def forbidden_error(error):
    background_image = url_for("static", filename="images/error_403.jpg")
    return render_template("errors/403.html", background_image=background_image), 403


@main_bp.app_errorhandler(404)
def not_found_error(error):
    background_image = url_for("static", filename="images/error_404.jpg")
    return render_template("errors/404.html", background_image=background_image), 404


@main_bp.app_errorhandler(500)
def internal_error(error):
    background_image = url_for("static", filename="images/error_500.jpg")
    return render_template("errors/500.html", background_image=background_image), 500


@main_bp.route("/")
def index():
    posts = Post.query.order_by(Post.posted_at.desc()).all()
    return render_template("main/index.html", posts=posts)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    posts = Post.query.order_by(Post.posted_at.desc()).all()
    return render_template("main/dashboard.html", posts=posts, user=current_user)


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = ContactMessage(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(message)
        db.session.commit()
        flash("Your message has been sent!", "success")
        return redirect(url_for("main.contact"))
    return render_template("main/contact.html", form=form)


@main_bp.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("main/view_post.html", post=post)


@main_bp.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("main/create_post.html", form=form)
