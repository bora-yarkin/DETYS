import os
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from app.models import Post, ContactMessage
from app.forms import PostForm, ContactForm, MarkAsReadForm, NotificationPreferencesForm
from app.core.extensions import db, csrf
from app.core.notifications import send_notification
from app.models import Notification
from werkzeug.utils import secure_filename

main_bp = Blueprint("main", __name__)

UPLOAD_FOLDER = "app/static/uploads"  # adjust if needed
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.app_errorhandler(403)
def forbidden_error(error):
    background_image = url_for("static", filename="images/error.jpg")
    return render_template("errors/403.html", background_image=background_image), 403


@main_bp.app_errorhandler(404)
def not_found_error(error):
    background_image = url_for("static", filename="images/error.jpg")
    return render_template("errors/404.html", background_image=background_image), 404


@main_bp.app_errorhandler(500)
def internal_error(error):
    background_image = url_for("static", filename="images/error.jpg")
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


@main_bp.route("/upload_image", methods=["POST"])
@login_required
@csrf.exempt
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file found"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        # The URL that the <img> tag will use. Since static is served from /static, adjust accordingly:
        file_url = url_for("static", filename="uploads/" + filename, _external=False)
        return jsonify({"url": file_url})
    else:
        return jsonify({"error": "File type not allowed"}), 400


@main_bp.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # form.content now contains the HTML from Quill
        post = Post(title=form.title.data, content=form.content.data, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("main/create_post.html", form=form)


@main_bp.route("/notifications")
@login_required
def notifications():
    unread = current_user.notifications.filter_by(is_read=False).order_by(Notification.created_at.desc()).all()
    read = current_user.notifications.filter_by(is_read=True).order_by(Notification.created_at.desc()).all()
    forms = {}
    for notification in unread:
        forms[notification.id] = MarkAsReadForm()

    return render_template("main/notifications.html", unread=unread, read=read, forms=forms)


@main_bp.route("/notifications/mark_read/<int:notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        abort(403)

    form = MarkAsReadForm()
    if form.validate_on_submit():
        notification.mark_as_read()
        flash("Notification marked as read.", "success")
    else:
        flash("Invalid request.", "danger")
    return redirect(url_for("main.notifications"))


@main_bp.route("/notifications/mark_all_read", methods=["POST"])
@login_required
def mark_all_notifications_read():
    unread_notifications = current_user.notifications.filter_by(is_read=False).all()
    for notification in unread_notifications:
        notification.mark_as_read()
    flash("All notifications marked as read.", "success")
    return redirect(url_for("main.notifications"))


@main_bp.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    form = NotificationPreferencesForm(obj=current_user.preferences)
    if form.validate_on_submit():
        current_user.preferences.receive_event_notifications = form.receive_event_notifications.data
        current_user.preferences.receive_membership_notifications = form.receive_membership_notifications.data
        current_user.preferences.receive_feedback_notifications = form.receive_feedback_notifications.data
        db.session.commit()
        flash("Your notification preferences have been updated.", "success")
        return redirect(url_for("main.preferences"))
    return render_template("main/preferences.html", form=form)
