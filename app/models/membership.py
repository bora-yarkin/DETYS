from app import db


class Membership(db.Model):
    __tablename__ = "memberships"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), primary_key=True)
    is_approved = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    user = db.relationship("User", back_populates="memberships")
    club = db.relationship("Club", back_populates="members")

    def __repr__(self):
        return f"<Membership User:{self.user_id} Club:{self.club_id}>"
