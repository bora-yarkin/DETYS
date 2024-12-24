from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required
from flask_wtf.csrf import generate_csrf
from app.core.extensions import db
from app.models import Club, ForumTopic, ForumPost, ForumCategory, ForumPostVote, ForumPoll, ForumPollChoice, Membership
from app.forms import ForumTopicForm, ForumPostForm, ForumPollForm
from app.core.decorators import club_member_required, club_member_or_manager_required

forum_bp = Blueprint("forum", __name__)


@forum_bp.route("/<int:club_id>/topics")
@login_required
def club_forum_topics(club_id):
    club = Club.query.get_or_404(club_id)
    category_id = request.args.get("category_id", type=int)
    query = ForumTopic.query.filter_by(club_id=club_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    topics = query.order_by(ForumTopic.created_at.desc()).all()

    categories = ForumCategory.query.order_by(ForumCategory.name.asc()).all()

    csrf_token = generate_csrf()
    return render_template("club/forum_topics.html", club=club, topics=topics, categories=categories, selected_category_id=category_id, csrf_token=csrf_token)


@forum_bp.route("/<int:club_id>/topics/create", methods=["GET", "POST"])
@login_required
@club_member_or_manager_required
def create_forum_topic(club_id):
    club = Club.query.get_or_404(club_id)
    form = ForumTopicForm()

    categories = ForumCategory.query.all()
    form.category_id.choices = [(0, "No Category")] + [(c.id, c.name) for c in categories]

    csrf_token = generate_csrf()

    if request.method == "POST":

        if form.validate_on_submit():
            selected_cat = form.category_id.data if form.category_id.data != 0 else None
            new_topic = ForumTopic(club_id=club_id, category_id=selected_cat, title=form.title.data, created_by=current_user.id)
            db.session.add(new_topic)
            db.session.flush()

            initial_post = ForumPost(topic_id=new_topic.id, user_id=current_user.id, content=form.content.data)
            db.session.add(initial_post)
            db.session.commit()

            flash("Forum topic created!", "success")
            return redirect(url_for("forum.club_forum_topics", club_id=club_id))

    return render_template("club/create_forum_topic.html", club=club, form=form, csrf_token=csrf_token)


@forum_bp.route("/topic/<int:topic_id>")
@login_required
def view_forum_topic(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    posts = ForumPost.query.filter_by(topic_id=topic_id).order_by(ForumPost.posted_at.asc()).all()

    poll = ForumPoll.query.filter_by(topic_id=topic.id).first()

    post_form = ForumPostForm()
    csrf_token = generate_csrf()

    return render_template("club/view_forum_topic.html", topic=topic, posts=posts, post_form=post_form, poll=poll, csrf_token=csrf_token)


@forum_bp.route("/topic/<int:topic_id>/post", methods=["POST"])
@login_required
def add_forum_post(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    club_id = topic.club_id

    membership = Membership.query.filter_by(club_id=club_id, user_id=current_user.id, is_approved=True).first()
    if not membership:
        abort(403)

    form = ForumPostForm()
    csrf_token = generate_csrf()

    if request.method == "POST":
        form_csrf = request.form.get("csrf_token")
        if not form_csrf or form_csrf != csrf_token:
            abort(400, "Invalid or missing CSRF token.")

        if form.validate_on_submit():
            post = ForumPost(topic_id=topic_id, user_id=current_user.id, content=form.content.data)
            db.session.add(post)
            db.session.commit()
            flash("Your post has been added.", "success")
        else:
            flash("Content cannot be empty.", "danger")

    return redirect(url_for("forum.view_forum_topic", topic_id=topic_id))


@forum_bp.route("/post/<int:post_id>/vote", methods=["POST"])
@login_required
def vote_forum_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    topic = post.topic
    club_id = topic.club_id

    from app.models import Membership

    membership = Membership.query.filter_by(club_id=club_id, user_id=current_user.id, is_approved=True).first()
    if not membership:
        abort(403)

    vote_type = request.form.get("vote_type", "up")
    if vote_type not in ["up", "down"]:
        abort(400, "Invalid vote_type")

    existing_vote = ForumPostVote.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if existing_vote:
        existing_vote.vote_type = vote_type
    else:
        new_vote = ForumPostVote(post_id=post_id, user_id=current_user.id, vote_type=vote_type)
        db.session.add(new_vote)
    db.session.commit()

    flash(f"You voted {vote_type} on post #{post_id}", "info")
    return redirect(url_for("forum.view_forum_topic", topic_id=topic.id))


@forum_bp.route("/topic/<int:topic_id>/poll/create", methods=["GET", "POST"])
@login_required
@club_member_required
def create_forum_poll(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    form = ForumPollForm()
    csrf_token = generate_csrf()

    if request.method == "POST":
        form_csrf = request.form.get("csrf_token")
        if not form_csrf or form_csrf != csrf_token:
            abort(400, "Invalid CSRF token.")

        if form.validate_on_submit():
            poll = ForumPoll(topic_id=topic.id, question=form.question.data)
            db.session.add(poll)
            db.session.flush()

            for choice_text in [form.choice1.data, form.choice2.data, form.choice3.data, form.choice4.data]:
                if choice_text:
                    db.session.add(ForumPollChoice(poll_id=poll.id, choice_text=choice_text))
            db.session.commit()

            flash("Poll created successfully!", "success")
            return redirect(url_for("forum.view_forum_topic", topic_id=topic.id))

    return render_template("club/create_forum_poll.html", topic=topic, form=form, csrf_token=csrf_token)


@forum_bp.route("/poll/<int:poll_id>/vote", methods=["POST"])
@login_required
def vote_forum_poll(poll_id):
    poll = ForumPoll.query.get_or_404(poll_id)
    topic = poll.topic
    club_id = topic.club_id

    membership = Membership.query.filter_by(club_id=club_id, user_id=current_user.id, is_approved=True).first()
    if not membership:
        abort(403)

    choice_id = request.form.get("choice_id")
    choice = ForumPollChoice.query.filter_by(id=choice_id, poll_id=poll_id).first()
    if not choice:
        flash("No choice selected or invalid choice.", "danger")
        return redirect(url_for("forum.view_forum_topic", topic_id=topic.id))

    choice.votes += 1
    db.session.commit()
    flash("Your vote has been recorded!", "success")
    return redirect(url_for("forum.view_forum_topic", topic_id=topic.id))
