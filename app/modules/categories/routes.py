from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from app.modules.categories.service import CategoryService
from app.modules.categories.models import Category
from  app import db

categories_bp = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories"
)


# =========================
# CREATE CATEGORY
# =========================
@categories_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_category():

    if request.method == "POST":

        name = request.form.get("name")
        parent_id = request.form.get("parent_id")

        if parent_id == "":
            parent_id = None

        CategoryService.create_category(
            tenant_id=current_user.tenant_id,
            name=name,
            parent_id=parent_id
        )

        flash("Category created successfully", "success")

        return redirect(url_for("categories.create_category"))

    categories = CategoryService.get_categories_by_tenant(
        current_user.tenant_id
    )

    return render_template(
        "categories/create.html",
        categories=categories
    )


# =========================
# LIST CATEGORIES
# =========================
@categories_bp.route("/")
@login_required
def list_categories():

    categories = CategoryService.get_categories_by_tenant(
        current_user.tenant_id
    )

    return render_template(
        "categories/list.html",
        categories=categories
    )
@categories_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(id):

    category = Category.query.get_or_404(id)

    if request.method == "POST":
        category.name = request.form.get("name")
        category.parent_id = request.form.get("parent_id") or None

        db.session.commit()

        flash("Category updated", "success")
        return redirect(url_for("categories.list_categories"))

    return render_template(
        "categories/edit.html",
        category=category
    )
@categories_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete_category(id):

    category = Category.query.get_or_404(id)

    db.session.delete(category)
    db.session.commit()

    flash("Category deleted", "success")

    return redirect(url_for("categories.create_category"))