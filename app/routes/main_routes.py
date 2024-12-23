import os
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from app.models import Club, Event, EventAttendance, EventResource, Membership, Poll, Post, ContactMessage, User
from app.forms import PostForm, ContactForm, MarkAsReadForm, NotificationPreferencesForm, MarkAllNotificationsReadForm
from app.core.extensions import db, csrf
from app.models import Notification
from werkzeug.utils import secure_filename

main_bp = Blueprint("main", __name__)

UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route("/")
def index():
    posts = Post.query.order_by(Post.posted_at.desc()).limit(3).all()
    all_clubs = Club.query.order_by(Club.name).all()
    all_events = Event.query.order_by(Event.date.asc()).all()
    return render_template("main/index.html", posts=posts, clubs=all_clubs, events=all_events)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user

    if user.is_main_admin:
        total_users = User.query.count()
        total_clubs = Club.query.count()
        total_events = Event.query.count()

        top_events = db.session.query(Event.title, db.func.count(EventAttendance.user_id)).join(EventAttendance, Event.id == EventAttendance.event_id).filter(EventAttendance.status == "confirmed").group_by(Event.id).order_by(db.func.count(EventAttendance.user_id).desc()).limit(5).all()

        resource_count = db.session.query(EventResource).join(Event, EventResource.event_id == Event.id).filter(Event.club_id.in_(club_ids)).count()

        poll_count = db.session.query(Poll).join(Event, Poll.event_id == Event.id).filter(Event.club_id.in_(club_ids)).count()
        dashboard_context = {
            "dashboard_mode": "admin",
            "total_users": total_users,
            "total_clubs": total_clubs,
            "total_events": total_events,
            "top_events": top_events,
            "resource_count": resource_count,
            "poll_count": poll_count,
        }

    elif user.is_club_manager:
        clubs_managed = Club.query.filter_by(president_id=user.id).all()
        club_ids = [club.id for club in clubs_managed]

        pending_membership_requests = Membership.query.filter(Membership.club_id.in_(club_ids), Membership.is_approved == False).count()

        upcoming_events = Event.query.filter(Event.club_id.in_(club_ids), Event.date >= db.func.now()).order_by(Event.date.asc()).limit(5).all()

        manager_top_events = (
            db.session.query(Event.title, db.func.count(EventAttendance.user_id))
            .join(EventAttendance, Event.id == EventAttendance.event_id)
            .filter(Event.club_id.in_(club_ids), EventAttendance.status == "confirmed")
            .group_by(Event.id)
            .order_by(db.func.count(EventAttendance.user_id).desc())
            .limit(5)
            .all()
        )
        resource_count = db.session.query(EventResource).join(Event, EventResource.event_id == Event.id).filter(Event.club_id.in_(club_ids)).count()

        poll_count = db.session.query(Poll).join(Event, Poll.event_id == Event.id).filter(Event.club_id.in_(club_ids)).count()

        dashboard_context = {
            "dashboard_mode": "manager",
            "clubs_managed": clubs_managed,
            "pending_membership_requests": pending_membership_requests,
            "upcoming_events": upcoming_events,
            "manager_top_events": manager_top_events,
            "resource_count": resource_count,
            "poll_count": poll_count,
        }

    else:
        user_events = EventAttendance.query.join(Event, EventAttendance.event_id == Event.id).filter(EventAttendance.user_id == user.id, EventAttendance.status.in_(["confirmed", "waiting"])).all()
        joined_clubs = Membership.query.join(Club, Membership.club_id == Club.id).filter(Membership.user_id == user.id, Membership.is_approved == True).all()

        bookmark_events = []
        bookmark_clubs = []
        for bm in user.bookmarks:
            if bm.event:
                bookmark_events.append(bm.event)
            elif bm.club:
                bookmark_clubs.append(bm.club)

        dashboard_context = {
            "dashboard_mode": "student",
            "user_events": user_events,
            "joined_clubs": joined_clubs,
            "bookmark_events": bookmark_events,
            "bookmark_clubs": bookmark_clubs,
        }

    return render_template("main/dashboard.html", user=user, **dashboard_context)


@main_bp.route("/posts")
def posts():
    all_posts = Post.query.order_by(Post.posted_at.desc()).all()
    return render_template("main/all_posts.html", posts=all_posts)


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
        file_url = url_for("static", filename="uploads/" + filename, _external=False)
        return jsonify({"url": file_url})
    else:
        return jsonify({"error": "File type not allowed"}), 400


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


@main_bp.route("/notifications")
@login_required
def notifications():
    unread = current_user.notifications.filter_by(is_read=False).order_by(Notification.created_at.desc()).all()
    read = current_user.notifications.filter_by(is_read=True).order_by(Notification.created_at.desc()).all()
    forms = {notification.id: MarkAsReadForm() for notification in unread}
    mark_all_form = MarkAllNotificationsReadForm()
    return render_template("main/notifications.html", unread=unread, read=read, forms=forms, mark_all_form=mark_all_form)


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


@main_bp.app_errorhandler(403)
@main_bp.app_errorhandler(404)
@main_bp.app_errorhandler(500)
def handle_errors(error):
    background_image = url_for("static", filename="images/error.jpg")
    error_code = error.code if hasattr(error, "code") else 500
    return render_template(f"errors/{error_code}.html", background_image=background_image), error_code
