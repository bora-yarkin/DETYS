# from app import db


# class Club(db.Model):
#     __tablename__ = "clubs"

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), unique=True, nullable=False)
#     description = db.Column(db.Text, nullable=True)
#     president_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
#     contact_email = db.Column(db.String(120), nullable=False)

#     # Relationships
#     president = db.relationship("User", backref="managed_clubs", foreign_keys=[president_id])
#     members = db.relationship("Membership", back_populates="club", cascade="all, delete-orphan")

#     def __repr__(self):
#         return f"<Club {self.name}>"


from app import db


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
