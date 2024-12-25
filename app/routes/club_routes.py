from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Club, Membership
from app.forms import ClubCreationForm
from app.core.extensions import db
from app.core.decorators import club_manager_required
from app.core.notifications import send_notification

club_bp = Blueprint("club", __name__)


@club_bp.route("/")
@login_required
def club_list():
    clubs = Club.query.all()
    return render_template("club/club_list.html", clubs=clubs)


@club_bp.route("/<int:club_id>")
@login_required
def club_detail(club_id):
    club = Club.query.get_or_404(club_id)
    is_member = False
    membership = None
    if current_user.is_authenticated:
        membership = Membership.query.filter_by(user_id=current_user.id, club_id=club.id).first()
        is_member = membership is not None and membership.is_approved
    return render_template("club/club_detail.html", club=club, is_member=is_member, membership=membership)


@club_bp.route("/create", methods=["GET", "POST"])
@login_required
@club_manager_required
def create_club():
    form = ClubCreationForm()
    if form.validate_on_submit():
        club = Club(name=form.name.data, description=form.description.data, contact_email=form.contact_email.data, president_id=current_user.id)
        db.session.add(club)
        db.session.commit()
        flash("Club created successfully!", "success")
        return redirect(url_for("club.club_list"))
    return render_template("club/create_club.html", form=form, is_edit=False)


@club_bp.route("/<int:club_id>/edit", methods=["GET", "POST"])
@login_required
@club_manager_required
def edit_club(club_id):
    club = Club.query.get_or_404(club_id)
    if club.president_id != current_user.id:
        abort(403)
    form = ClubCreationForm(obj=club, club_id=club_id)
    if form.validate_on_submit():
        form.populate_obj(club)
        db.session.commit()
        flash("Club updated successfully!", "success")
        return redirect(url_for("club.club_detail", club_id=club_id))
    return render_template("club/edit_club.html", form=form, is_edit=True, club=club)


@club_bp.route("/<int:club_id>/delete", methods=["POST"])
@login_required
@club_manager_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    if club.president_id != current_user.id:
        abort(403)
    try:
        db.session.delete(club)
        db.session.commit()
        flash("Club deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting club: {str(e)}", "danger")
    return redirect(url_for("club.club_list"))


@club_bp.route("/<int:club_id>/confirm_delete", methods=["GET", "POST"])
@login_required
@club_manager_required
def confirm_delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    if club.president_id != current_user.id:
        abort(403)
    return render_template("club/confirm_delete.html", club=club)


@club_bp.route("/<int:club_id>/join")
@login_required
def join_club(club_id):
    club = Club.query.get_or_404(club_id)
    existing_membership = Membership.query.filter_by(user_id=current_user.id, club_id=club.id).first()
    if existing_membership:
        flash("You have already requested to join or are a member of this club.", "info")
    else:
        membership = Membership(user_id=current_user.id, club_id=club.id)
        db.session.add(membership)
        db.session.commit()
        flash("Membership request sent to the club manager.", "success")
    return redirect(url_for("club.club_detail", club_id=club_id))


@club_bp.route("/<int:club_id>/members")
@login_required
@club_manager_required
def manage_members(club_id):
    club = Club.query.get_or_404(club_id)
    if club.president_id != current_user.id:
        abort(403)
    pending_members = Membership.query.filter_by(club_id=club_id, is_approved=False).all()
    approved_members = Membership.query.filter_by(club_id=club_id, is_approved=True).all()
    return render_template("club/manage_members.html", club=club, pending_members=pending_members, approved_members=approved_members)


@club_bp.route("/<int:club_id>/approve/<int:user_id>")
@login_required
@club_manager_required
def approve_member(club_id, user_id):
    club = Club.query.get_or_404(club_id)
    if club.president_id != current_user.id:
        abort(403)
    membership = Membership.query.filter_by(club_id=club_id, user_id=user_id).first_or_404()
    membership.is_approved = True
    db.session.commit()
    flash("Member approved successfully.", "success")
    send_notification(user_id=user_id, message=f"Your membership request for {club.name} has been approved!", notification_type="success")
    return redirect(url_for("club.manage_members", club_id=club_id))


@club_bp.route("/<int:club_id>/remove/<int:user_id>")
@login_required
@club_manager_required
def remove_member(club_id, user_id):
    club = Club.query.get_or_404(club_id)
    if club.president_id != current_user.id:
        abort(403)
    membership = Membership.query.filter_by(club_id=club_id, user_id=user_id).first_or_404()
    db.session.delete(membership)
    db.session.commit()
    flash("Member removed successfully.", "success")
    return redirect(url_for("club.manage_members", club_id=club_id))
