from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default="student")  # Roles: student, club_manager, main_admin

    # Relationships
    memberships = db.relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    managed_clubs = db.relationship("Club", back_populates="president", foreign_keys="Club.president_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # User role verification methods
    def is_student(self):
        return self.role == "student"

    def is_club_manager(self):
        return self.role == "club_manager"

    def is_main_admin(self):
        return self.role == "main_admin"

    def __repr__(self):
        return f"<User {self.username}>"


# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
