from app import db


class EventAttendance(db.Model):
    __tablename__ = "event_attendance"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), primary_key=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    registered_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    user = db.relationship("User", back_populates="event_attendances")
    event = db.relationship("Event", back_populates="attendees")

    def __repr__(self):
        return f"<EventAttendance User:{self.user_id} Event:{self.event_id}>"
