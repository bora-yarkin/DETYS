from flask import Blueprint, render_template, redirect, request, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Club, ClubMessage, Membership
from app.forms import ClubCreationForm, ClubMessageForm
from app.core.extensions import db
from app.core.decorators import admin_or_manager_required
from app.core.notifications import send_notification

# Club blueprint'i oluşturur
club_bp = Blueprint("club", __name__)


# Kulüp listesini görüntüler
@club_bp.route("/")
@login_required
def club_list():
    # Tüm kulüpleri sorgular
    clubs = Club.query.all()
    # Kulüp listesini club/club_list.html şablonuna gönderir
    return render_template("club/club_list.html", clubs=clubs)


# Kulüp detaylarını görüntüler ve mesaj gönderir
@club_bp.route("/<int:club_id>", methods=["GET", "POST"])
@login_required
def club_detail(club_id):
    # Belirtilen ID'ye sahip kulübü veritabanından sorgular, yoksa 404 hatası döner
    club = Club.query.get_or_404(club_id)
    is_member = False
    membership = None
    # Kullanıcı giriş yapmışsa üyelik durumunu kontrol eder
    if current_user.is_authenticated:
        membership = Membership.query.filter_by(user_id=current_user.id, club_id=club.id).first()
        is_member = membership is not None and membership.is_approved

    form = ClubMessageForm()
    # Form gönderildiğinde ve doğrulama başarılı olduğunda
    if form.validate_on_submit():
        # Kullanıcı kulüp başkanı değilse veya ana yönetici değilse 403 hatası döner
        if club.president_id != current_user.id and not current_user.is_main_admin:
            abort(403)
        # Yeni mesaj oluşturur ve veritabanına ekler
        message = ClubMessage(club_id=club.id, user_id=current_user.id, content=form.content.data)
        db.session.add(message)
        db.session.commit()
        flash("Message posted successfully.", "success")
        return redirect(url_for("club.club_detail", club_id=club.id))

    # Sayfa numarasını alır ve mesajları sayfalar
    page = request.args.get("page", 1, type=int)
    messages = ClubMessage.query.filter_by(club_id=club.id).order_by(ClubMessage.timestamp.desc()).paginate(page=page, per_page=10)

    # Kulüp detaylarını ve mesajları club/club_detail.html şablonuna gönderir
    return render_template("club/club_detail.html", club=club, is_member=is_member, membership=membership, form=form, messages=messages)


# Yeni kulüp oluşturur
@club_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_or_manager_required
def create_club():
    form = ClubCreationForm()
    # Form gönderildiğinde ve doğrulama başarılı olduğunda
    if form.validate_on_submit():
        # Yeni kulüp oluşturur ve veritabanına ekler
        club = Club(name=form.name.data, description=form.description.data, contact_email=form.contact_email.data, president_id=current_user.id)
        db.session.add(club)
        db.session.commit()
        flash("Club created successfully!", "success")
        return redirect(url_for("club.club_list"))
    # Kulüp oluşturma formunu club/create_club.html şablonuna gönderir
    return render_template("club/create_club.html", form=form, is_edit=False)


# Kulüp bilgilerini düzenler
@club_bp.route("/<int:club_id>/edit", methods=["GET", "POST"])
@login_required
@admin_or_manager_required
def edit_club(club_id):
    # Belirtilen ID'ye sahip kulübü veritabanından sorgular, yoksa 404 hatası döner
    club = Club.query.get_or_404(club_id)
    # Kullanıcı kulüp başkanı değilse veya ana yönetici değilse 403 hatası döner
    if club.president_id != current_user.id and not current_user.is_main_admin:
        abort(403)
    form = ClubCreationForm(obj=club, club_id=club_id)
    # Form gönderildiğinde ve doğrulama başarılı olduğunda
    if form.validate_on_submit():
        # Kulüp bilgilerini günceller ve değişiklikleri veritabanına kaydeder
        form.populate_obj(club)
        db.session.commit()
        flash("Club updated successfully!", "success")
        return redirect(url_for("club.club_detail", club_id=club_id))
    # Kulüp düzenleme formunu club/edit_club.html şablonuna gönderir
    return render_template("club/edit_club.html", form=form, is_edit=True, club=club)


# Kulübü siler
@club_bp.route("/<int:club_id>/delete", methods=["POST"])
@login_required
@admin_or_manager_required
def delete_club(club_id):
    # Belirtilen ID'ye sahip kulübü veritabanından sorgular, yoksa 404 hatası döner
    club = Club.query.get_or_404(club_id)
    # Kullanıcı kulüp başkanı değilse veya ana yönetici değilse 403 hatası döner
    if club.president_id != current_user.id and not current_user.is_main_admin:
        abort(403)
    try:
        # Kulübü veritabanından siler
        db.session.delete(club)
        db.session.commit()
        flash("Club deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting club: {str(e)}", "danger")
    # Kulüp listesine yönlendirir
    return redirect(url_for("club.club_list"))


# Kulübe katılma isteği gönderir
@club_bp.route("/<int:club_id>/join")
@login_required
def join_club(club_id):
    # Belirtilen ID'ye sahip kulübü veritabanından sorgular, yoksa 404 hatası döner
    club = Club.query.get_or_404(club_id)
    # Kullanıcının mevcut üyelik isteği olup olmadığını kontrol eder
    existing_membership = Membership.query.filter_by(user_id=current_user.id, club_id=club.id).first()
    if existing_membership:
        flash("You have already requested to join or are a member of this club.", "info")
    else:
        # Yeni üyelik isteği oluşturur ve veritabanına ekler
        membership = Membership(user_id=current_user.id, club_id=club.id)
        db.session.add(membership)
        db.session.commit()
        flash("Membership request sent to the club manager.", "success")
    # Kulüp detaylarına yönlendirir
    return redirect(url_for("club.club_detail", club_id=club_id))


# Kulüp üyelerini yönetir
@club_bp.route("/<int:club_id>/members")
@login_required
@admin_or_manager_required
def manage_members(club_id):
    # Belirtilen ID'ye sahip kulübü veritabanından sorgular, yoksa 404 hatası döner
    club = Club.query.get_or_404(club_id)
    # Kullanıcı kulüp başkanı değilse veya ana yönetici değilse 403 hatası döner
    if club.president_id != current_user.id and not current_user.is_main_admin:
        abort(403)
    # Onay bekleyen ve onaylanmış üyelikleri sorgular
    pending_members = Membership.query.filter_by(club_id=club_id, is_approved=False).all()
    approved_members = Membership.query.filter_by(club_id=club_id, is_approved=True).all()
    # Üyelik bilgilerini club/manage_members.html şablonuna gönderir
    return render_template("club/manage_members.html", club=club, pending_members=pending_members, approved_members=approved_members)


# Üyelik isteğini onaylar
@club_bp.route("/<int:club_id>/approve/<int:user_id>")
@login_required
@admin_or_manager_required
def approve_member(club_id, user_id):
    # Belirtilen ID'ye sahip kulübü veritabanından sorgular, yoksa 404 hatası döner
    club = Club.query.get_or_404(club_id)
    # Kullanıcı kulüp başkanı değilse veya ana yönetici değilse 403 hatası döner
    if club.president_id != current_user.id and not current_user.is_main_admin:
        abort(403)
    # Belirtilen kullanıcıya ait üyelik isteğini sorgular, yoksa 404 hatası döner
    membership = Membership.query.filter_by(club_id=club_id, user_id=user_id).first_or_404()
    # Üyelik isteğini onaylar ve değişiklikleri veritabanına kaydeder
    membership.is_approved = True
    db.session.commit()
    flash("Member approved successfully.", "success")
    # Kullanıcıya bildirim gönderir
    send_notification(user_id=user_id, message=f"Your membership request for {club.name} has been approved!", notification_type="success")
    # Üye yönetim sayfasına yönlendirir
    return redirect(url_for("club.manage_members", club_id=club_id))


# Üyeyi kulüpten çıkarır
@club_bp.route("/<int:club_id>/remove/<int:user_id>")
@login_required
@admin_or_manager_required
def remove_member(club_id, user_id):
    # Belirtilen ID'ye sahip kulübü veritabanından sorgular, yoksa 404 hatası döner
    club = Club.query.get_or_404(club_id)
    # Kullanıcı kulüp başkanı değilse veya ana yönetici değilse 403 hatası döner
    if club.president_id != current_user.id and not current_user.is_main_admin:
        abort(403)
    # Belirtilen kullanıcıya ait üyeliği sorgular, yoksa 404 hatası döner
    membership = Membership.query.filter_by(club_id=club_id, user_id=user_id).first_or_404()
    # Üyeliği veritabanından siler ve değişiklikleri kaydeder
    db.session.delete(membership)
    db.session.commit()
    flash("Member removed successfully.", "success")
    # Üye yönetim sayfasına yönlendirir
    return redirect(url_for("club.manage_members", club_id=club_id))
