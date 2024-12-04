from app.sockets.notification_socket import send_notification_to_user, broadcast_notification


def some_action():
    # TODO: Implement this function
    user_id = 1
    message = "You have a new message!"
    send_notification_to_user(user_id, message)


def create_event(form_data, current_user):
    # TODO: Implement this function
    message = f"New event '{form_data['title']}' created by {current_user.username}!"
    broadcast_notification(message)
