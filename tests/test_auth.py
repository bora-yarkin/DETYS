import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com", role="student")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        return user

def test_registration(client):
    response = client.post("/auth/register", data={
        "username": "newuser",
        "email": "new@example.com",
        "role": "student",
        "password": "password",
        "confirm": "password"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

def test_login(client, user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Logged in successfully" in response.data
