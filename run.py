# from app import create_app
# from app.extensions import socketio
# import eventlet
# import eventlet.wsgi

# app = create_app()

# if __name__ == "__main__":
#     # Use eventlet's WSGI server to enable WebSocket support
#     eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)

# run.py

from app import create_app
from app.utils.extensions import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True)
