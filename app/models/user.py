from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default="student")  # Current Available Roles: student, club_manager, main_admin

    # Relationships
    memberships = db.relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    managed_clubs = db.relationship("Club", back_populates="president", foreign_keys="Club.president_id")
    event_attendances = db.relationship("EventAttendance", back_populates="user", cascade="all, delete-orphan")
    event_feedbacks = db.relationship("EventFeedback", back_populates="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_student(self):
        return self.role == "student"

    @property
    def is_club_manager(self):
        return self.managed_clubs is not None and len(self.managed_clubs) > 0

    @property
    def managed_club_id(self):
        if self.is_club_manager:
            return self.managed_clubs[0].id
        return None

    @property
    def is_main_admin(self):
        return self.role == "main_admin"

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
