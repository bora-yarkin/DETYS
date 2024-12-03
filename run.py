# from app import create_app, socketio

# app = create_app()

# if __name__ == "__main__":
#     app.run(debug=True)
#     socketio.run(app, debug=True)


from app import create_app

app = create_app()

if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi
    from app.extensions import socketio

    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
