from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from app.core.extensions import db
from app.models import Club, ForumTopic, ForumPost
from app.forms import ForumTopicForm, ForumPostForm
from app.core.decorators import club_manager_required, student_required

forum_bp = Blueprint("forum", __name__)


@forum_bp.route("/<int:club_id>/topics")
@login_required
def club_forum_topics(club_id):
    club = Club.query.get_or_404(club_id)
    topics = ForumTopic.query.filter_by(club_id=club_id).order_by(ForumTopic.created_at.desc()).all()
    return render_template("club/forum_topics.html", club=club, topics=topics)


@forum_bp.route("/<int:club_id>/topics/create", methods=["GET", "POST"])
@login_required
def create_forum_topic(club_id):
    club = Club.query.get_or_404(club_id)
    form = ForumTopicForm()
    if form.validate_on_submit():
        topic = ForumTopic(club_id=club_id, title=form.title.data, created_by=current_user.id)
        db.session.add(topic)
        db.session.commit()
        flash("Forum topic created!", "success")
        return redirect(url_for("forum.club_forum_topics", club_id=club_id))
    return render_template("club/create_forum_topic.html", club=club, form=form)


@forum_bp.route("/topic/<int:topic_id>")
@login_required
def view_forum_topic(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    posts = ForumPost.query.filter_by(topic_id=topic_id).order_by(ForumPost.posted_at.asc()).all()
    return render_template("club/view_forum_topic.html", topic=topic, posts=posts)


@forum_bp.route("/topic/<int:topic_id>/post", methods=["POST"])
@login_required
def add_forum_post(topic_id):
    content = request.form.get("content")
    if content:
        post = ForumPost(topic_id=topic_id, user_id=current_user.id, content=content)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been added.", "success")
    return redirect(url_for("forum.view_forum_topic", topic_id=topic_id))
