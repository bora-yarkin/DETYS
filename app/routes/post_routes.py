import os
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.models import Post
from app.forms import PostForm
from app.core.extensions import db, csrf
from werkzeug.utils import secure_filename

# Post blueprint'i oluşturur
post_bp = Blueprint("post", __name__)

UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


# Dosya uzantısının izin verilenler arasında olup olmadığını kontrol eder
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Gönderiyi düzenleme veya silme yetkisini kontrol eder
def can_edit_or_delete_post(post):
    if current_user.is_main_admin:
        return True
    if current_user.is_club_manager and post.author_id == current_user.id:
        return True
    return False


# Tüm gönderileri görüntüler
@post_bp.route("/posts")
def posts():
    # Tüm gönderileri tarihe göre sıralayarak sorgular
    all_posts = Post.query.order_by(Post.posted_at.desc()).all()
    # Gönderi listesini post/all_posts.html şablonuna gönderir
    return render_template("post/all_posts.html", posts=all_posts)


# Belirli bir gönderiyi görüntüler
@post_bp.route("/post/<int:post_id>")
def view_post(post_id):
    # Belirtilen ID'ye sahip gönderiyi veritabanından sorgular, yoksa 404 hatası döner
    post = Post.query.get_or_404(post_id)
    # Gönderi detaylarını post/view_post.html şablonuna gönderir
    return render_template("post/view_post.html", post=post)


# Yeni gönderi oluşturur
@post_bp.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # Yeni gönderi oluşturur ve veritabanına ekler
        post = Post(title=form.title.data, content=form.content.data, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for("main.dashboard"))
    # Gönderi oluşturma formunu post/create_post.html şablonuna gönderir
    return render_template("post/create_post.html", form=form)


# Gönderiyi düzenler
@post_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    # Belirtilen ID'ye sahip gönderiyi veritabanından sorgular, yoksa 404 hatası döner
    post = Post.query.get_or_404(post_id)
    if not can_edit_or_delete_post(post):
        abort(403)

    form = PostForm(obj=post)
    if form.validate_on_submit():
        # Gönderi bilgilerini günceller ve değişiklikleri veritabanına kaydeder
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for("post.view_post", post_id=post.id))

    # Gönderi düzenleme formunu post/edit_post.html şablonuna gönderir
    return render_template("post/edit_post.html", form=form, post=post)


# Gönderiyi siler
@post_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    # Belirtilen ID'ye sahip gönderiyi veritabanından sorgular, yoksa 404 hatası döner
    post = Post.query.get_or_404(post_id)
    if not can_edit_or_delete_post(post):
        abort(403)
    try:
        # Gönderiyi veritabanından siler
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting post: {str(e)}", "danger")

    return redirect(url_for("post.posts"))


# Görsel yükler
@post_bp.route("/upload_image", methods=["POST"])
@login_required
@csrf.exempt
def upload_image():
    # Dosya yükleme formunda dosya olup olmadığını kontrol eder
    if "file" not in request.files:
        return jsonify({"error": "No file found"}), 400

    file = request.files["file"]
    # Dosya seçilmemişse hata mesajı gösterir
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Dosya geçerli ve izin verilen türdeyse
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        file_url = url_for("static", filename="uploads/" + filename, _external=False)
        return jsonify({"url": file_url})
    else:
        return jsonify({"error": "File type not allowed"}), 400
