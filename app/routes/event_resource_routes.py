import os
from flask import Blueprint, request, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from app.core.extensions import db
from app.models import Event, EventResource
from werkzeug.utils import secure_filename

resource_bp = Blueprint("resource", __name__)

UPLOAD_FOLDER = "app/static/event_resources"
ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "png", "jpg", "jpeg", "xlsx"}


# Dosya uzantısının izin verilenler arasında olup olmadığını kontrol eder
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Etkinlik kaynağı yükleme işlemi
@resource_bp.route("/<int:event_id>/upload", methods=["POST"])
@login_required
def upload_resource(event_id):
    # Belirtilen ID'ye sahip etkinliği veritabanından sorgular, yoksa 404 hatası döner
    event = Event.query.get_or_404(event_id)
    # Kullanıcı etkinlik kulübünün başkanı değilse veya ana yönetici değilse yetkisiz erişim hatası döner
    if event.club.president_id != current_user.id and not current_user.is_main_admin:
        flash("You are not authorized to upload resources for this event.", "danger")
        return redirect(url_for("event.event_detail", event_id=event_id))

    # Dosya yükleme formunda dosya olup olmadığını kontrol eder
    if "file" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("event.event_detail", event_id=event_id))
    file = request.files["file"]
    # Dosya seçilmemişse hata mesajı gösterir
    if file.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for("event.event_detail", event_id=event_id))

    # Dosya geçerli ve izin verilen türdeyse
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Yeni kaynak oluşturur ve veritabanına ekler
        new_resource = EventResource(event_id=event_id, filename=filename, filepath=filepath)
        db.session.add(new_resource)
        db.session.commit()
        flash("Resource uploaded successfully.", "success")
    else:
        flash("File type not allowed.", "danger")

    return redirect(url_for("event.event_detail", event_id=event_id))


# Etkinlik kaynağı indirme işlemi
@resource_bp.route("/download/<int:resource_id>")
@login_required
def download_resource(resource_id):
    # Belirtilen ID'ye sahip kaynağı veritabanından sorgular, yoksa 404 hatası döner
    resource = EventResource.query.get_or_404(resource_id)
    directory = os.path.dirname(resource.filepath)
    filename = os.path.basename(resource.filepath)
    # Kaynağı belirtilen dizinden indirir
    return send_from_directory(directory=directory, path=filename, as_attachment=True)
