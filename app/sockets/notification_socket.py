from app.extensions import socketio


@socketio.on("connect")
def handle_connect():
    print("A client has connected")
