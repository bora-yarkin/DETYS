import os
from flask import Blueprint, request, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from app.core.extensions import db, csrf
from app.models import Event, EventResource
from werkzeug.utils import secure_filename

resource_bp = Blueprint("resource", __name__)

UPLOAD_FOLDER = "app/static/event_resources"
ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "png", "jpg", "jpeg", "xlsx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@resource_bp.route("/<int:event_id>/upload", methods=["POST"])
@login_required
def upload_resource(event_id):
    event = Event.query.get_or_404(event_id)
    # only the club manager who owns this event can upload
    if event.club.president_id != current_user.id and not current_user.is_main_admin:
        flash("You are not authorized to upload resources for this event.", "danger")
        return redirect(url_for("event.event_detail", event_id=event_id))

    if "file" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("event.event_detail", event_id=event_id))
    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for("event.event_detail", event_id=event_id))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        new_resource = EventResource(event_id=event_id, filename=filename, filepath=filepath)
        db.session.add(new_resource)
        db.session.commit()
        flash("Resource uploaded successfully.", "success")
    else:
        flash("File type not allowed.", "danger")

    return redirect(url_for("event.event_detail", event_id=event_id))


@resource_bp.route("/download/<int:resource_id>")
@login_required
def download_resource(resource_id):
    resource = EventResource.query.get_or_404(resource_id)
    directory = os.path.dirname(resource.filepath)
    filename = os.path.basename(resource.filepath)
    return send_from_directory(directory=directory, path=filename, as_attachment=True)
