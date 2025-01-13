from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.core.extensions import db
from app.models import Event, Poll, PollChoice
from app.core.decorators import admin_or_manager_required

poll_bp = Blueprint("poll", __name__)


# Yeni anket oluşturma
@poll_bp.route("/<int:event_id>/create", methods=["GET", "POST"])
@login_required
@admin_or_manager_required
def create_poll(event_id):
    # Belirtilen ID'ye sahip etkinliği veritabanından sorgular, yoksa 404 hatası döner
    event = Event.query.get_or_404(event_id)
    # Kullanıcı etkinlik kulübünün başkanı değilse veya ana yönetici değilse yetkisiz erişim hatası döner
    if event.club.president_id != current_user.id and not current_user.is_main_admin:
        flash("You don't have permission to create a poll for this event.", "danger")
        return redirect(url_for("event.event_detail", event_id=event.id))

    # Anket oluşturma formu gönderildiğinde
    if request.method == "POST":
        # Anket sorusunu ve seçeneklerini formdan alır
        question = request.form.get("question")
        choices = request.form.getlist("choice[]")
        # Anket sorusu boşsa hata mesajı gösterir
        if not question.strip():
            flash("Poll question is required.", "danger")
            return redirect(request.url)
        # Yeni anket oluşturur ve veritabanına ekler
        new_poll = Poll(event_id=event_id, question=question.strip())
        db.session.add(new_poll)
        db.session.flush()

        # Anket seçeneklerini oluşturur ve veritabanına ekler
        for text in choices:
            text = text.strip()
            if text:
                db.session.add(PollChoice(poll_id=new_poll.id, choice_text=text))

        db.session.commit()
        flash("Poll created successfully!", "success")
        return redirect(url_for("event.event_detail", event_id=event.id))

    # Anket oluşturma formunu poll/create_poll.html şablonuna gönderir
    return render_template("poll/create_poll.html", event=event)


# Anket görüntüleme
@poll_bp.route("/<int:poll_id>")
@login_required
def view_poll(poll_id):
    # Belirtilen ID'ye sahip anketi ve ilgili etkinliği veritabanından sorgular, yoksa 404 hatası döner
    poll = Poll.query.get_or_404(poll_id)
    event = Event.query.get_or_404(poll.event_id)
    # Anketin toplam oy sayısını hesaplar
    total_votes = sum(choice.votes for choice in poll.choices)

    # Anket ve etkinlik bilgilerini poll/view_poll.html şablonuna gönderir
    return render_template("poll/view_poll.html", poll=poll, event=event, total_votes=total_votes)


# Anket oylama
@poll_bp.route("/<int:poll_id>/vote", methods=["POST"])
@login_required
def vote_poll(poll_id):
    # Belirtilen ID'ye sahip anketi veritabanından sorgular, yoksa 404 hatası döner
    poll = Poll.query.get_or_404(poll_id)
    # Seçilen anket seçeneğinin ID'sini formdan alır
    choice_id = request.form.get("choice_id")
    # Seçenek ID'si yoksa hata mesajı gösterir
    if not choice_id:
        flash("No choice selected.", "danger")
        return redirect(url_for("poll.view_poll", poll_id=poll.id))

    # Belirtilen ID'ye sahip anket seçeneğini sorgular, yoksa 404 hatası döner
    choice = PollChoice.query.filter_by(id=choice_id, poll_id=poll_id).first_or_404()
    # Seçeneğin oy sayısını artırır ve değişiklikleri veritabanına kaydeder
    choice.votes += 1
    db.session.commit()
    flash("Your vote has been recorded!", "success")
    return redirect(url_for("poll.view_poll", poll_id=poll.id))
