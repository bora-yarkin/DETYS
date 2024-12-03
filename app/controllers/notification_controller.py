from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room
from app.extensions import socketio
from flask_login import current_user, login_required

notification_bp = Blueprint("notification_bp", __name__)


@socketio.on("join")
@login_required
def handle_join(data):
    room = data.get("room")
    if room:
        join_room(room)
        print(f"User {current_user.username} joined room {room}")
    else:
        print("No room specified to join.")


def send_notification(user_id, message):
    room = f"user_{user_id}"
    socketio.emit("notification", {"msg": message}, room=room)
