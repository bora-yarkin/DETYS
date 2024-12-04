from app import create_app
from app.extensions import socketio
import eventlet
import eventlet.wsgi

app = create_app()

if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
