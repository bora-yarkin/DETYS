from app.extensions import socketio
from flask_socketio import join_room
from flask_login import current_user


@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)
