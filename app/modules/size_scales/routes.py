from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from app.extensions import db

from app.modules.size_scales.models import (
    SizeScale,
    SizeScaleItem
)

from app.modules.size_scales.service import SizeScaleService
import pandas as pd

size_scales_bp = Blueprint(
    "size_scales",
    __name__,
    url_prefix="/size-scales"
)


# =====================================================
# CREATE SCALE
# =====================================================
# =====================================================
# CREATE SCALE
# =====================================================
@size_scales_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_scale():

    if request.method == "GET":
        scales = SizeScale.query.filter_by(
            tenant_id=current_user.tenant_id
        ).all()

        return render_template(
            "size_scales/create.html",
            scales=scales
        )

    name = request.form.get("name")
    file = request.files.get("file")

    if not name:
        return "Scale name required", 400

    scale = SizeScale(
        name=name,
        tenant_id=current_user.tenant_id
    )

    db.session.add(scale)
    db.session.flush()

    sizes = []

    # =========================
    # CASE 1: EXCEL UPLOAD
    # =========================
    if file and file.filename.endswith(".xlsx"):

        df = pd.read_excel(file)

        if "size" not in df.columns:
            return "Excel must contain 'size' column", 400

        for i, row in df.iterrows():

            if pd.isna(row["size"]):
                continue

            sizes.append(str(row["size"]).strip())

    # =========================
    # CASE 2: MANUAL INPUT
    # =========================
    else:

        sizes = request.form.getlist("sizes[]")

    # =========================
    # SAVE SIZES
    # =========================
    for index, size_value in enumerate(sizes):

        item = SizeScaleItem(
            scale_id=scale.id,
            value=size_value,
            sort_order=index
        )

        db.session.add(item)

    db.session.commit()

    return redirect(url_for("size_scales.create_scale"))


# =====================================================
# MANAGE SCALE
# =====================================================
@size_scales_bp.route(
    "/<int:scale_id>/manage",
    methods=["GET", "POST"]
)
@login_required
def manage_scale(scale_id):

    scale = SizeScale.query.get_or_404(scale_id)

    if scale.tenant_id != current_user.tenant_id:
        flash("Unauthorized", "danger")
        return redirect(
            url_for("size_scales.create_scale")
        )

    if request.method == "POST":

        value = request.form.get("value")

        # AUTO SORT ORDER
        last_item = SizeScaleItem.query.filter_by(
            size_scale_id=scale.id
        ).order_by(
            SizeScaleItem.sort_order.desc()
        ).first()

        next_order = 1

        if last_item:
            next_order = last_item.sort_order + 1

        size_item = SizeScaleItem(
            size_scale_id=scale.id,
            value=value,
            sort_order=next_order
        )

        db.session.add(size_item)
        db.session.commit()

        flash("Size added", "success")

        return redirect(
            url_for(
                "size_scales.manage_scale",
                scale_id=scale.id
            )
        )

    return render_template(
        "size_scales/manage.html",
        scale=scale
    )


# =====================================================
# EDIT SCALE
# =====================================================
@size_scales_bp.route(
    "/<int:id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_scale(id):

    scale = SizeScale.query.get_or_404(id)

    if scale.tenant_id != current_user.tenant_id:
        flash("Unauthorized", "danger")
        return redirect(
            url_for("size_scales.create_scale")
        )

    if request.method == "POST":

        scale.name = request.form.get("name")
        scale.category = request.form.get("category")

        db.session.commit()

        flash("Scale updated", "success")

        return redirect(
            url_for("size_scales.create_scale")
        )

    return render_template(
        "size_scales/edit.html",
        scale=scale
    )


# =====================================================
# DELETE SCALE
# =====================================================
@size_scales_bp.route(
    "/<int:id>/delete",
    methods=["POST"]
)
@login_required
def delete_scale(id):

    scale = SizeScale.query.get_or_404(id)

    if scale.tenant_id != current_user.tenant_id:
        flash("Unauthorized", "danger")
        return redirect(
            url_for("size_scales.create_scale")
        )

    # DELETE ITEMS FIRST
    SizeScaleItem.query.filter_by(
        size_scale_id=scale.id
    ).delete()

    db.session.delete(scale)
    db.session.commit()

    flash("Scale deleted", "success")

    return redirect(
        url_for("size_scales.create_scale")
    )

@size_scales_bp.route("/sizes/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_size(id):

    size = SizeScaleItem.query.get_or_404(id)

    scale = SizeScale.query.get_or_404(size.size_scale_id)

    if scale.tenant_id != current_user.tenant_id:
        flash("Unauthorized", "danger")
        return redirect(url_for("size_scales.create_scale"))

    if request.method == "POST":

        value = request.form.get("value", "").strip()

        if not value:
            flash("Value cannot be empty", "danger")
            return redirect(url_for("size_scales.edit_size", id=id))

        size.value = value
        db.session.commit()

        flash("Size updated", "success")

        return redirect(
            url_for("size_scales.manage_scale", scale_id=scale.id)
        )

    return render_template(
        "size_scales/edit_size.html",
        size=size
    )
# =====================================================
# DELETE SIZE ITEM
# =====================================================
@size_scales_bp.route(
    "/sizes/<int:id>/delete",
    methods=["POST"]
)
@login_required
def delete_size(id):

    size = SizeScaleItem.query.get_or_404(id)

    scale_id = size.size_scale_id

    db.session.delete(size)
    db.session.commit()

    # REORDER REMAINING SIZES
    remaining_sizes = SizeScaleItem.query.filter_by(
        size_scale_id=scale_id
    ).order_by(
        SizeScaleItem.sort_order
    ).all()

    for index, item in enumerate(
        remaining_sizes,
        start=1
    ):
        item.sort_order = index

    db.session.commit()

    flash(
        "Size deleted successfully",
        "success"
    )

    return redirect(
        url_for(
            "size_scales.manage_scale",
            scale_id=scale_id
        )
    )