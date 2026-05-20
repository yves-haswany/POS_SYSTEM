from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import login_required, current_user

from app.modules.categories.service import CategoryService
from app.modules.categories.models import Category
from  app import db
import pandas as pd

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
@categories_bp.route("/import-excel", methods=["POST"])
@login_required
def import_categories_excel():

    try:
        file = request.files.get("file")

        if not file:
            return "No file uploaded", 400

        df = pd.read_excel(file)

        if "name" not in df.columns:
            return "Missing column: name", 400

        created = 0

        # cache to avoid duplicate DB queries
        category_cache = {}

        def get_or_create_category(name, parent=None):

            key = (name, parent.id if parent else None)

            if key in category_cache:
                return category_cache[key]

            cat = Category.query.filter_by(
                name=name,
                parent_id=parent.id if parent else None
            ).first()

            if not cat:
                cat = Category(
                    name=name,
                    parent_id=parent.id if parent else None,
                    tenant_id=current_user.tenant_id
                )
                db.session.add(cat)
                db.session.flush()

            category_cache[key] = cat
            return cat

        for _, row in df.iterrows():

            name = str(row["name"]).strip()

            parent_name = (
                str(row["parent_name"]).strip()
                if "parent_name" in row
                and not pd.isna(row["parent_name"])
                else None
            )

            parent = None

            if parent_name:
                parent = Category.query.filter_by(
                    name=parent_name,
                    tenant_id=current_user.tenant_id
                ).first()

                # optionally auto-create parent
                if not parent:
                    parent = Category(
                        name=parent_name,
                        tenant_id=current_user.tenant_id
                    )
                    db.session.add(parent)
                    db.session.flush()

            get_or_create_category(name, parent)

            created += 1

        db.session.commit()

        return jsonify({
            "message": "Categories imported successfully",
            "created": created
        })

    except Exception as e:
        db.session.rollback()
        return str(e), 500