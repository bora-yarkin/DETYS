from app import create_app

app = create_app()

with app.app_context():
    from app.models import db, User, Club, Membership, Event, EventAttendance, EventFeedback, Post, Notification, EventResource, Poll, PollChoice, Bookmark, Category, ClubMessage
    from faker import Faker
    from werkzeug.security import generate_password_hash
    import random
    from datetime import datetime

    fake = Faker()

    def populate_users(n=100):
        for _ in range(n):
            user = User(username=fake.user_name(), email=fake.email(), password_hash=generate_password_hash("password123"), role=random.choice(["student", "club_manager", "main_admin"]))
            db.session.add(user)
        db.session.commit()
        print(f"Added {n} users.")

    def populate_categories(n=10):
        for _ in range(n):
            category = Category(name=fake.word().capitalize(), created_at=fake.date_time_between(start_date="-2y", end_date="now"))
            db.session.add(category)
        db.session.commit()
        print(f"Added {n} categories.")

    def populate_clubs(n=50):
        users = User.query.all()
        for _ in range(n):
            club = Club(name=fake.company(), description=fake.paragraph(nb_sentences=3), president_id=random.choice(users).id, contact_email=fake.company_email())
            db.session.add(club)
        db.session.commit()
        print(f"Added {n} clubs.")

    def populate_memberships(n=200):
        users = User.query.all()
        clubs = Club.query.all()
        existing_memberships = set()

        # Keep trying until we have n unique memberships
        attempts = 0
        while len(existing_memberships) < n and attempts < n * 2:
            user_id = random.choice(users).id
            club_id = random.choice(clubs).id
            membership_key = (user_id, club_id)

            if membership_key not in existing_memberships:
                existing_memberships.add(membership_key)
                membership = Membership(user_id=user_id, club_id=club_id, is_approved=random.choice([True, False]), joined_at=fake.date_time_between(start_date="-2y", end_date="now"))
                db.session.add(membership)

            attempts += 1

        db.session.commit()
        print(f"Added {len(existing_memberships)} memberships.")

    def populate_events(n=200):
        clubs = Club.query.all()
        categories = Category.query.all()
        for _ in range(n):
            event = Event(
                title=fake.sentence(nb_words=6),
                description=fake.paragraph(nb_sentences=5),
                date=fake.date_time_between(start_date="now", end_date="+1y"),
                location=fake.address(),
                capacity=random.randint(50, 500),
                club_id=random.choice(clubs).id,
                category_id=random.choice(categories).id if categories else None,
            )
            db.session.add(event)
        db.session.commit()
        print(f"Added {n} events.")

    def populate_event_attendance(n=500):
        users = User.query.all()
        events = Event.query.all()
        existing_attendances = set()
        statuses = ["confirmed", "waiting"]

        attempts = 0
        while len(existing_attendances) < n and attempts < n * 2:
            user_id = random.choice(users).id
            event_id = random.choice(events).id
            attendance_key = (user_id, event_id)

            if attendance_key not in existing_attendances:
                existing_attendances.add(attendance_key)
                event = Event.query.get(event_id)
                
                confirmed_count = EventAttendance.query.filter_by(
                    event_id=event_id, 
                    status="confirmed"
                ).count()
                
                status = "confirmed" if confirmed_count < event.capacity else "waiting"
                
                attendance = EventAttendance(
                    user_id=user_id,
                    event_id=event_id,
                    status=status,
                    registered_at=fake.date_time_between(start_date="-1y", end_date="now")
                )
                db.session.add(attendance)

            attempts += 1

        db.session.commit()
        print(f"Added {len(existing_attendances)} event attendances.")

    def populate_event_feedback(n=300):
        users = User.query.all()
        events = Event.query.all()
        for _ in range(n):
            feedback = EventFeedback(event_id=random.choice(events).id, user_id=random.choice(users).id, rating=random.randint(1, 5), comment=fake.text(max_nb_chars=200), submitted_at=fake.date_time_between(start_date="-2y", end_date="now"))
            db.session.add(feedback)
        db.session.commit()
        print(f"Added {n} event feedbacks.")

    def populate_posts(n=150):
        users = User.query.all()
        for _ in range(n):
            post = Post(title=fake.sentence(nb_words=6), content=fake.paragraph(nb_sentences=10), posted_at=fake.date_time_between(start_date="-2y", end_date="now"), author_id=random.choice(users).id)
            db.session.add(post)
        db.session.commit()
        print(f"Added {n} posts.")

    def populate_notifications(n=200):
        users = User.query.all()
        notification_types = ["info", "warning", "alert"]
        for _ in range(n):
            notification = Notification(user_id=random.choice(users).id, message=fake.sentence(nb_words=10), notification_type=random.choice(notification_types), created_at=fake.date_time_between(start_date="-2y", end_date="now"), is_read=random.choice([True, False]))
            db.session.add(notification)
        db.session.commit()
        print(f"Added {n} notifications.")

    def populate_categories(n=10):
        for _ in range(n):
            category = Category(name=fake.word().capitalize(), created_at=fake.date_time_between(start_date="-2y", end_date="now"))
            db.session.add(category)
        db.session.commit()
        print(f"Added {n} categories.")

    def populate_event_resources(n=300):
        events = Event.query.all()
        for _ in range(n):
            resource = EventResource(event_id=random.choice(events).id, filename=fake.file_name(extension="pdf"), upload_date=fake.date_time_between(start_date="-2y", end_date="now"), filepath=fake.file_path())
            db.session.add(resource)
        db.session.commit()
        print(f"Added {n} event resources.")

    def populate_polls(n=50):
        events = Event.query.all()
        for _ in range(n):
            poll = Poll(event_id=random.choice(events).id, question=fake.sentence(nb_words=10), created_at=fake.date_time_between(start_date="-2y", end_date="now"))
            db.session.add(poll)
        db.session.commit()
        print(f"Added {n} polls.")

    def populate_poll_choices(n=200):
        polls = Poll.query.all()
        for _ in range(n):
            choice = PollChoice(poll_id=random.choice(polls).id, choice_text=fake.word(), votes=random.randint(0, 100))
            db.session.add(choice)
        db.session.commit()
        print(f"Added {n} poll choices.")

    def populate_bookmarks(n=250):
        users = User.query.all()
        events = Event.query.all()
        clubs = Club.query.all()
        for _ in range(n):
            bookmark = Bookmark(user_id=random.choice(users).id, event_id=random.choice(events).id if random.choice([True, False]) else None, club_id=random.choice(clubs).id if random.choice([True, False]) else None, created_at=fake.date_time_between(start_date="-2y", end_date="now"))
            db.session.add(bookmark)
        db.session.commit()
        print(f"Added {n} bookmarks.")

    def populate_club_messages(n=100):
        clubs = Club.query.all()
        users = User.query.all()
        for _ in range(n):
            message = ClubMessage(club_id=random.choice(clubs).id, user_id=random.choice(users).id, content=fake.sentence(nb_words=15), timestamp=fake.date_time_between(start_date="-2y", end_date="now"))
            db.session.add(message)
        db.session.commit()
        print(f"Added {n} club messages.")

    def main():
        db.drop_all()
        db.create_all()

        populate_users()
        populate_categories()
        populate_clubs()
        populate_memberships()
        populate_events()
        populate_event_attendance()
        populate_event_feedback()
        populate_posts()
        populate_notifications()
        populate_event_resources()
        populate_polls()
        populate_poll_choices()
        populate_bookmarks()
        populate_club_messages()
        print("Random data population completed.")

    if __name__ == "__main__":
        with app.app_context():
            main()
