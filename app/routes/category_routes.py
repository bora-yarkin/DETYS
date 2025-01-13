from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.core.extensions import db
from app.models import Category
from app.core.decorators import main_admin_required

category_bp = Blueprint("category", __name__)


# Kategorileri listeleme
@category_bp.route("/categories")
@login_required
@main_admin_required
def list_categories():
    # Tüm kategorileri isimlerine göre sıralayarak sorgular
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("category/list_categories.html", categories=categories)


# Kategori oluşturma
@category_bp.route("/categories/create", methods=["GET", "POST"])
@login_required
@main_admin_required
def create_category():
    if request.method == "POST":
        # Formdan kategori adını alır ve boşlukları temizler
        name = request.form.get("name", "").strip()
        # Kategori adı boşsa hata mesajı gösterir
        if not name:
            flash("Category name is required.", "danger")
            return redirect(request.url)

        # Aynı ada sahip bir kategori olup olmadığını kontrol eder
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash("A category with that name already exists.", "danger")
            return redirect(request.url)

        # Yeni kategori oluşturur ve veritabanına ekler
        cat = Category(name=name)
        db.session.add(cat)
        db.session.commit()
        flash("Category created successfully!", "success")
        return redirect(url_for("category.list_categories"))

    return render_template("category/create_category.html")


# Kategori düzenleme
@category_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
@main_admin_required
def edit_category(category_id):
    cat = Category.query.get_or_404(category_id)
    if request.method == "POST":
        # Formdan kategori adını alır ve boşlukları temizler
        name = request.form.get("name", "").strip()
        if not name:
            flash("Category name is required.", "danger")
            return redirect(request.url)

        # Aynı ada sahip başka bir kategori olup olmadığını kontrol eder
        existing = Category.query.filter(Category.name == name, Category.id != cat.id).first()
        if existing:
            flash("A category with that name already exists.", "danger")
            return redirect(request.url)

        # Kategori adını günceller ve değişiklikleri veritabanına kaydeder
        cat.name = name
        db.session.commit()
        flash("Category updated successfully!", "success")
        return redirect(url_for("category.list_categories"))

    return render_template("category/edit_category.html", cat=cat)


# Kategori silme
@category_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@main_admin_required
def delete_category(category_id):
    cat = Category.query.get_or_404(category_id)
    db.session.delete(cat)
    db.session.commit()
    flash("Category deleted.", "success")
    return redirect(url_for("category.list_categories"))
