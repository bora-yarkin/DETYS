from app import db


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

    def __repr__(self):
        return f"<Event {self.title}>"
