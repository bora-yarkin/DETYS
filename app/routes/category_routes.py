from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.core.extensions import db
from app.models import Category
from app.core.decorators import main_admin_required

category_bp = Blueprint("category", __name__)


@category_bp.route("/categories")
@login_required
@main_admin_required
def list_categories():
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template("category/list_categories.html", categories=categories)


@category_bp.route("/categories/create", methods=["GET", "POST"])
@login_required
@main_admin_required
def create_category():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Category name is required.", "danger")
            return redirect(request.url)

        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash("A category with that name already exists.", "danger")
            return redirect(request.url)

        cat = Category(name=name)
        db.session.add(cat)
        db.session.commit()
        flash("Category created successfully!", "success")
        return redirect(url_for("category.list_categories"))

    return render_template("category/create_category.html")


@category_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
@main_admin_required
def edit_category(category_id):
    cat = Category.query.get_or_404(category_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Category name is required.", "danger")
            return redirect(request.url)

        existing = Category.query.filter(Category.name == name, Category.id != cat.id).first()
        if existing:
            flash("A category with that name already exists.", "danger")
            return redirect(request.url)

        cat.name = name
        db.session.commit()
        flash("Category updated successfully!", "success")
        return redirect(url_for("category.list_categories"))

    return render_template("category/edit_category.html", cat=cat)


@category_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@main_admin_required
def delete_category(category_id):
    cat = Category.query.get_or_404(category_id)
    db.session.delete(cat)
    db.session.commit()
    flash("Category deleted.", "success")
    return redirect(url_for("category.list_categories"))
