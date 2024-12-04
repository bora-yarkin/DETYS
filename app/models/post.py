from app import db
from datetime import datetime


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", name="fk_posts_author_id"), nullable=False)

    # Relationships
    author = db.relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post '{self.title}'>"
