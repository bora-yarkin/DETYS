import unittest
from app import create_app, db
from app.models import User


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_registration(self):
        response = self.client.post("/auth/register", data={"username": "testuser", "email": "test@example.com", "role": "student", "password": "password", "confirm": "password", "submit": True}, follow_redirects=True)
        self.assertIn(b"Registration successful", response.data)

    def test_login(self):
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com", role="student")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
        response = self.client.post("/auth/login", data={"username": "testuser", "password": "password", "submit": True}, follow_redirects=True)
        self.assertIn(b"Logged in successfully", response.data)
