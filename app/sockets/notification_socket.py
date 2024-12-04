# from app.extensions import socketio


# @socketio.on("connect")
# def handle_connect():
#     print("A client has connected")

# app/sockets/notification_socket.py

from app.extensions import socketio
from flask_socketio import join_room, leave_room, emit
from flask_login import current_user


@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        room = f"user_{current_user.id}"
        join_room(room)
        print(f"User {current_user.username} connected and joined room {room}")


@socketio.on("disconnect")
def handle_disconnect():
    if current_user.is_authenticated:
        room = f"user_{current_user.id}"
        leave_room(room)
        print(f"User {current_user.username} disconnected and left room {room}")


def send_notification_to_user(user_id, message):
    room = f"user_{user_id}"
    socketio.emit("notification", {"msg": message}, room=room)


def broadcast_notification(message):
    socketio.emit("notification", {"msg": message}, broadcast=True)


# Send a success notification
# socketio.emit("notification", {"msg": message, "type": "success"}, room=room)
# socket.on('notification', function (data) {
#     toastr[data.type](data.msg);
# });
