from app.core.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.Index("idx_user_username", "username"),
        db.Index("idx_user_email", "email"),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default="student")

    # Relationships
    memberships = db.relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    managed_clubs = db.relationship("Club", back_populates="president", foreign_keys="Club.president_id")
    event_attendances = db.relationship("EventAttendance", back_populates="user", cascade="all, delete-orphan")
    event_feedbacks = db.relationship("EventFeedback", back_populates="user", lazy="dynamic")
    posts = db.relationship("Post", back_populates="author", lazy="dynamic")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_student(self):
        return self.role == "student"

    @property
    def is_club_manager(self):
        return self.role == "club_manager"

    @property
    def is_main_admin(self):
        return self.role == "main_admin"

    @property
    def managed_club_id(self):
        if self.is_club_manager and self.managed_clubs:
            return self.managed_clubs[0].id
        return None

    @property
    def unread_notifications_count(self):
        return self.notifications.filter_by(is_read=False).count()

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    president_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)

    # Relationships
    president = db.relationship("User", back_populates="managed_clubs", foreign_keys=[president_id])
    members = db.relationship("Membership", back_populates="club", cascade="all, delete-orphan")
    events = db.relationship("Event", back_populates="club", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Club {self.name}>"


class Membership(db.Model):
    __tablename__ = "memberships"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), primary_key=True)
    is_approved = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="memberships")
    club = db.relationship("Club", back_populates="members")

    def __repr__(self):
        return f"<Membership User:{self.user_id} Club:{self.club_id}>"


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    # Relationships
    club = db.relationship("Club", back_populates="events")
    attendees = db.relationship("EventAttendance", back_populates="event", cascade="all, delete-orphan")
    feedbacks = db.relationship("EventFeedback", back_populates="event", lazy="dynamic")
    category = db.relationship("Category", back_populates="events", lazy="joined")

    def __repr__(self):
        return f"<Event {self.title}>"


class EventAttendance(db.Model):
    __tablename__ = "event_attendance"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), primary_key=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="event_attendances")
    event = db.relationship("Event", back_populates="attendees")

    def __repr__(self):
        return f"<EventAttendance User:{self.user_id} Event:{self.event_id}>"


class EventFeedback(db.Model):
    __tablename__ = "event_feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="event_feedbacks")
    event = db.relationship("Event", back_populates="feedbacks")

    def __repr__(self):
        return f"<EventFeedback User:{self.user_id} Event:{self.event_id}>"


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relationships
    author = db.relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post '{self.title}'>"


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContactMessage from {self.name}>"


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False, default="info")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # Explicit back_populates relationship
    user = db.relationship("User", back_populates="notifications")

    def mark_as_read(self):
        self.is_read = True
        db.session.commit()

    def __repr__(self):
        return f"<Notification id={self.id}, user_id={self.user_id}, type={self.notification_type}, is_read={self.is_read}>"


class ForumCategory(db.Model):
    __tablename__ = "forum_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to topics
    topics = db.relationship("ForumTopic", back_populates="forum_category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ForumCategory {self.name}>"


class ForumTopic(db.Model):
    __tablename__ = "forum_topics"
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("forum_categories.id"), nullable=True)  # new
    title = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Existing relationships
    club = db.relationship("Club", backref="forum_topics")
    posts = db.relationship("ForumPost", backref="topic", cascade="all, delete-orphan")
    forum_category = db.relationship("ForumCategory", back_populates="topics", lazy="joined")
    forum_polls = db.relationship("ForumPoll", back_populates="topic", cascade="all, delete-orphan")
    creator = db.relationship("User", backref="topics_created", foreign_keys=[created_by])

    def __repr__(self):
        return f"<ForumTopic {self.title}>"


class ForumPost(db.Model):
    __tablename__ = "forum_posts"
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("forum_topics.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    votes = db.relationship("ForumPostVote", back_populates="post", cascade="all, delete-orphan")

    user = db.relationship("User")

    @property
    def score(self):
        up = sum(1 for v in self.votes if v.vote_type == "up")
        down = sum(1 for v in self.votes if v.vote_type == "down")
        return up - down

    def __repr__(self):
        return f"<ForumPost id={self.id} topic_id={self.topic_id}>"


class ForumPostVote(db.Model):
    __tablename__ = "forum_post_votes"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("forum_posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # "up" or "down"
    vote_type = db.Column(db.String(10), nullable=False, default="up")

    post = db.relationship("ForumPost", back_populates="votes")
    user = db.relationship("User")

    def __repr__(self):
        return f"<ForumPostVote post_id={self.post_id}, user_id={self.user_id}, type={self.vote_type}>"


class ForumPoll(db.Model):
    __tablename__ = "forum_polls"
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("forum_topics.id"), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    topic = db.relationship("ForumTopic", back_populates="forum_polls")
    choices = db.relationship("ForumPollChoice", back_populates="poll", cascade="all, delete-orphan")


class ForumPollChoice(db.Model):
    __tablename__ = "forum_poll_choices"
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("forum_polls.id"), nullable=False)
    choice_text = db.Column(db.String(255), nullable=False)
    votes = db.Column(db.Integer, default=0)

    poll = db.relationship("ForumPoll", back_populates="choices")


class EventResource(db.Model):
    __tablename__ = "event_resources"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    # optional: store the file path or relative path
    filepath = db.Column(db.String(255), nullable=False)

    event = db.relationship("Event", backref="resources")


class Poll(db.Model):
    __tablename__ = "polls"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    choices = db.relationship("PollChoice", backref="poll", cascade="all, delete-orphan")
    event = db.relationship("Event", backref="polls")


class PollChoice(db.Model):
    __tablename__ = "poll_choices"
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("polls.id"), nullable=False)
    choice_text = db.Column(db.String(255), nullable=False)
    votes = db.Column(db.Integer, default=0)


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="bookmarks")
    event = db.relationship("Event", backref="bookmarks")
    club = db.relationship("Club", backref="bookmarks")


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Event
    events = db.relationship("Event", back_populates="category", cascade="all, delete-orphan")
