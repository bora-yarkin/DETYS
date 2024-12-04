from .extensions import db, login_manager
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
    role = db.Column(db.String(20), nullable=False, default="student")  # Roles: 'student', 'club_manager', 'main_admin'

    # Relationships
    memberships = db.relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    managed_clubs = db.relationship("Club", back_populates="president", foreign_keys="Club.president_id")
    event_attendances = db.relationship("EventAttendance", back_populates="user", cascade="all, delete-orphan")
    event_feedbacks = db.relationship("EventFeedback", back_populates="user", lazy="dynamic")
    posts = db.relationship("Post", back_populates="author", lazy="dynamic")

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

    # Relationships
    club = db.relationship("Club", back_populates="events")
    attendees = db.relationship("EventAttendance", back_populates="event", cascade="all, delete-orphan")
    feedbacks = db.relationship("EventFeedback", back_populates="event", lazy="dynamic")

    def __repr__(self):
        return f"<Event {self.title}>"


class EventAttendance(db.Model):
    __tablename__ = "event_attendance"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), primary_key=True)
    status = db.Column(db.String(20), nullable=False, default="pending")  # Statuses: 'confirmed', 'waiting', 'pending'
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
