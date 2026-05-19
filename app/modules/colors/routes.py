from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.modules.colors.models import Color
import hashlib

colors_bp = Blueprint("colors", __name__, url_prefix="/colors")


# =====================================================
# 🎯 Helper: auto-generate hex from name
# =====================================================
# =====================================================
# 🎨 PREDEFINED COLORS
# =====================================================
PREDEFINED_COLORS = {
    "red": "#FF0000",
    "blue": "#0000FF",
    "green": "#008000",
    "yellow": "#FFFF00",
    "black": "#000000",
    "white": "#FFFFFF",
    "gray": "#808080",
    "grey": "#808080",
    "orange": "#FFA500",
    "purple": "#800080",
    "pink": "#FFC0CB",
    "brown": "#A52A2A",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "lime": "#00FF00",
    "navy": "#000080",
    "teal": "#008080",
    "olive": "#808000",
    "maroon": "#800000",
    "silver": "#C0C0C0",
    "gold": "#FFD700",
    "beige": "#F5F5DC",
    "ivory": "#FFFFF0",
    "coral": "#FF7F50",
    "turquoise": "#40E0D0"
}


# =====================================================
# 🎯 GENERATE HEX FROM NAME
# =====================================================
def name_to_hex(name: str) -> str:

    key = name.strip().lower()

    # RETURN REAL COLOR
    if key in PREDEFINED_COLORS:
        return PREDEFINED_COLORS[key]

    # FALLBACK HASH
    hash_obj = hashlib.md5(name.encode())

    return f"#{hash_obj.hexdigest()[:6].upper()}"


# =====================================================
# 📋 LIST COLORS
# =====================================================
@colors_bp.route("/")
@login_required
def list_colors():

    colors = Color.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(
        "colors/list.html",
        colors=colors
    )


# =====================================================
# ➕ CREATE COLOR
# =====================================================
@colors_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_color():

    if request.method == "POST":

        name = request.form.get("name")

        if not name:
            flash("Name is required", "danger")

            return redirect(
                url_for("colors.create_color")
            )

        hex_code = name_to_hex(name)

        color = Color(
            name=name,
            hex_code=hex_code,
            tenant_id=current_user.tenant_id
        )

        db.session.add(color)
        db.session.commit()

        flash(
            "Color created successfully",
            "success"
        )

        # RELOAD SAME PAGE
        return redirect(
            url_for("colors.create_color")
        )

    # LOAD COLORS FOR TEMPLATE
    colors = Color.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(
        "colors/create.html",
        colors=colors
    )


# =====================================================
# ✏️ EDIT COLOR
# =====================================================
@colors_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_color(id):

    color = Color.query.filter_by(
        id=id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    if request.method == "POST":

        name = request.form.get("name")

        if not name:
            flash("Name is required", "danger")
            return redirect(url_for("colors.edit_color", id=id))

        color.name = name
        color.hex_code = name_to_hex(name)

        db.session.commit()

        flash("Color updated successfully", "success")
        return redirect(url_for("colors.list_colors"))

    return render_template(
        "colors/edit.html",
        color=color
    )


# =====================================================
# 🗑️ DELETE COLOR
# =====================================================
@colors_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete_color(id):

    color = Color.query.filter_by(
        id=id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    db.session.delete(color)
    db.session.commit()

    flash("Color deleted successfully", "success")

    return redirect(url_for("colors.create_color"))