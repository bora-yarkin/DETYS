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

def test_registration(client):
    response = client.post("/login", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
        "confirm": "password",
        "action": "register"
    }, follow_redirects=True)
    assert b"Registration successful" in response.data

def test_login(client):
    with client.application.app_context():
        user = User(username="testuser", email="test@example.com", role="student")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
    
    response = client.post("/login", data={
        "username": "testuser",
        "password": "password",
        "action": "login"
    }, follow_redirects=True)
    assert b"Login Successful" in response.data
