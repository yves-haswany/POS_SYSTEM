from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    current_user,
    login_required
)

from app.extensions import db

from .service import ProductVariantService

from app.modules.products.models import Product
from app.modules.product_variants.models import ProductVariant
from app.modules.colors.models import Color
from app.modules.size_scales.models import SizeScale


variants_bp = Blueprint(
    "product_variants",
    __name__,
    url_prefix="/variants"
)


# ==========================================
# API CREATE
# ==========================================
@variants_bp.route("/", methods=["POST"])
def create_variant():

    data = request.json

    variant = ProductVariantService.create_variant(
        data
    )

    return jsonify({
        "id": variant.id
    })


# ==========================================
# API LIST BY PRODUCT
# ==========================================
@variants_bp.route(
    "/product/<int:product_id>"
)
def get_by_product(product_id):

    variants = ProductVariantService.get_by_product(
        product_id
    )

    return jsonify(
        [v.id for v in variants]
    )


# ==========================================
# VARIANT CREATE PAGE
# ==========================================
@variants_bp.route(
    "/create/<int:product_id>",
    methods=["GET"]
)
@login_required
def create_variant_page(product_id):

    product = Product.query.get_or_404(
        product_id
    )

    return render_template(
        "products/variant_create.html",
        product=product
    )


# ==========================================
# VARIANT MATRIX
# ==========================================
@variants_bp.route(
    "/matrix/<int:product_id>",
    methods=["GET", "POST"]
)
@login_required
def variant_matrix(product_id):

    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    colors = Color.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    size_scales = SizeScale.query.all()

    if request.method == "POST":

        try:

            # ==========================
            # SAVE SIZE SCALE
            # ==========================
            scale_id = request.form.get(
                "size_scale_id"
            )

            if scale_id:

                product.size_scale_id = int(
                    scale_id
                )

            # ==========================
            # SIZE ONLY
            # ==========================
            if (
                product.has_size
                and
                not product.has_color
            ):

                selected_sizes = request.form.getlist(
                    "selected_sizes"
                )

                for size_id in selected_sizes:

                    qty = int(
                        request.form.get(
                            f"qty_size_{size_id}",
                            0
                        )
                    )

                    barcode = request.form.get(
                        f"barcode_size_{size_id}",
                        ""
                    )

                    existing = ProductVariant.query.filter_by(
                        product_id=product.id,
                        size_id=int(size_id)
                    ).first()

                    if existing:
                        continue

                    variant = ProductVariant(

                        product_id=product.id,

                        tenant_id=product.tenant_id,

                        size_scale_id=product.size_scale_id,

                        size_id=int(size_id),

                        quantity=qty,

                        barcode=barcode
                    )

                    db.session.add(
                        variant
                    )

            # ==========================
            # COLOR ONLY
            # ==========================
            elif (
                product.has_color
                and
                not product.has_size
            ):

                selected_colors = request.form.getlist(
                    "selected_colors"
                )

                for color_id in selected_colors:

                    qty = int(
                        request.form.get(
                            f"qty_color_{color_id}",
                            0
                        )
                    )

                    barcode = request.form.get(
                        f"barcode_color_{color_id}",
                        ""
                    )

                    existing = ProductVariant.query.filter_by(
                        product_id=product.id,
                        color_id=int(color_id)
                    ).first()

                    if existing:
                        continue

                    variant = ProductVariant(

                        product_id=product.id,

                        tenant_id=product.tenant_id,

                        color_id=int(
                            color_id
                        ),

                        quantity=qty,

                        barcode=barcode
                    )

                    db.session.add(
                        variant
                    )

            # ==========================
            # SIZE + COLOR
            # ==========================
            elif (
                product.has_size
                and
                product.has_color
            ):

                selected_sizes = request.form.getlist(
                    "selected_sizes"
                )

                for size_id in selected_sizes:

                    selected_colors = request.form.getlist(
                        f"color_{size_id}"
                    )

                    for color_id in selected_colors:

                        qty = int(
                            request.form.get(
                                f"qty_{size_id}_{color_id}",
                                0
                            )
                        )

                        barcode = request.form.get(
                            f"barcode_{size_id}_{color_id}",
                            ""
                        )

                        existing = ProductVariant.query.filter_by(

                            product_id=product.id,

                            size_id=int(
                                size_id
                            ),

                            color_id=int(
                                color_id
                            )

                        ).first()

                        if existing:
                            continue

                        variant = ProductVariant(

                            product_id=product.id,

                            tenant_id=product.tenant_id,

                            size_scale_id=product.size_scale_id,

                            size_id=int(
                                size_id
                            ),

                            color_id=int(
                                color_id
                            ),

                            quantity=qty,

                            barcode=barcode
                        )

                        db.session.add(
                            variant
                        )

            # ==========================
            # ACTIVATE PRODUCT
            # ==========================
            product.is_draft = False

            product.is_active = True

            db.session.commit()

            flash(
                "Variants saved successfully",
                "success"
            )

            return redirect(
                url_for(
                    "tenant.dashboard"
                )
            )

        except Exception as e:

            db.session.rollback()

            flash(
                str(e),
                "danger"
            )

    return render_template(

        "product_variants/matrix.html",

        product=product,

        colors=colors,

        size_scales=size_scales
    )