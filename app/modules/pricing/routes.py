from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from app.extensions import db

from app.modules.pricing.models import PriceList, PriceListItem
from app.modules.pricing.service import PricingService
from app.modules.products.models import Product
from app.modules.product_variants.models import ProductVariant


pricing_bp = Blueprint(
    "pricing",
    __name__,
    url_prefix="/pricing"
)


# =========================================================
# GET SINGLE PRICE (API)
# =========================================================
@pricing_bp.route("/price", methods=["GET"])
def get_price():

    variant_id = request.args.get("variant_id", type=int)
    price_list_id = request.args.get("price_list_id", type=int)

    if variant_id is None or price_list_id is None:
        return jsonify({
            "error": "missing parameters",
            "required": ["variant_id", "price_list_id"]
        }), 400

    price = PricingService.get_price(variant_id, price_list_id)

    if price is None:
        return jsonify({
            "error": "price not found",
            "variant_id": variant_id,
            "price_list_id": price_list_id
        }), 404

    return jsonify({
        "variant_id": variant_id,
        "price_list_id": price_list_id,
        "price": price
    })


# =========================================================
# LOAD VARIANTS FOR PRODUCT
# =========================================================
@pricing_bp.route("/product-variants", methods=["GET"])
@login_required
def product_variants():

    product_id = request.args.get("product_id", type=int)

    if not product_id:
        return jsonify([])

    variants = ProductVariant.query.filter_by(
        product_id=product_id
    ).all()

    result = []

    for v in variants:

        attrs = []

        if hasattr(v, "size") and v.size:
            if hasattr(v.size, "label"):
                size_label = v.size.label
            elif hasattr(v.size, "value"):
                size_label = v.size.value
            elif hasattr(v.size, "code"):
                size_label = v.size.code
            else:
                size_label = str(v.size.id)

            attrs.append(f"Size: {size_label}")

        if hasattr(v, "color") and v.color:
            attrs.append(f"Color: {v.color.name}")

        if not attrs:
            attrs.append(v.sku or f"Variant {v.id}")

        result.append({
            "id": v.id,
            "product": v.product.name,
            "price": v.price,
            "attributes": " | ".join(attrs)
        })

    return jsonify(result)


# =========================================================
# LIST PRICE LISTS
# =========================================================
@pricing_bp.route("/price-lists", methods=["GET"])
@login_required
def list_price_lists():

    price_lists = PriceList.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(
        "pricing/price_lists_list.html",
        price_lists=price_lists
    )


# =========================================================
# CREATE PRICE LIST
# =========================================================
@pricing_bp.route("/price-lists/create", methods=["GET", "POST"])
@login_required
def create_price_list():

    # -----------------------------
    # GET
    # -----------------------------
    if request.method == "GET":

        products = Product.query.filter_by(
            tenant_id=current_user.tenant_id
        ).all()

        price_lists = PriceList.query.filter_by(
            tenant_id=current_user.tenant_id
        ).all()

        return render_template(
            "pricing/price_lists.html",
            products=products,
            price_lists=price_lists
        )

    # -----------------------------
    # POST
    # -----------------------------
    name = request.form.get("name")
    currency = request.form.get("currency")

    if not name or not currency:
        flash("Name and currency required", "error")
        return redirect(url_for("pricing.create_price_list"))

    price_list = PriceList(
        name=name,
        currency=currency,
        tenant_id=current_user.tenant_id
    )

    db.session.add(price_list)
    db.session.flush()

    # save selected variant prices
    for key, value in request.form.items():

        if key.startswith("price_") and value:

            variant_id = int(key.replace("price_", ""))

            db.session.add(PriceListItem(
                price_list_id=price_list.id,
                product_variant_id=variant_id,
                price=float(value)
            ))

    db.session.commit()

    flash("Price list created", "success")

    return redirect(url_for("pricing.list_price_lists"))


# =========================================================
# VIEW PRICE LIST
# =========================================================
@pricing_bp.route("/price-lists/<int:price_list_id>", methods=["GET"])
@login_required
def view_price_list(price_list_id):

    price_list = PriceList.query.filter_by(
        id=price_list_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    return render_template(
        "pricing/price_list_detail.html",
        price_list=price_list
    )


# =========================================================
# EDIT PRICE LIST
# =========================================================
@pricing_bp.route(
    "/price-lists/<int:price_list_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_price_list(price_list_id):

    price_list = PriceList.query.filter_by(
        id=price_list_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    # =====================================
    # GET
    # =====================================

    if request.method == "GET":

        products = Product.query.filter_by(
            tenant_id=current_user.tenant_id
        ).all()

        return render_template(
            "pricing/edit_price_list.html",
            price_list=price_list,
            products=products
        )

    # =====================================
    # UPDATE BASIC INFO
    # =====================================

    name = request.form.get(
        "name",
        ""
    ).strip()

    currency = request.form.get(
        "currency",
        ""
    ).strip()

    if not name or not currency:

        flash(
            "Name and currency required",
            "error"
        )

        return redirect(
            url_for(
                "pricing.edit_price_list",
                price_list_id=price_list.id
            )
        )

    price_list.name = name
    price_list.currency = currency

    try:

        # remove existing items

        PriceListItem.query.filter_by(
            price_list_id=price_list.id
        ).delete()

        added = 0

        # rebuild list

        for key, value in request.form.items():

            if not key.startswith(
                "price_"
            ):
                continue

            if not value:
                continue

            variant_id = int(
                key.replace(
                    "price_",
                    ""
                )
            )

            variant = ProductVariant.query.get(
                variant_id
            )

            if not variant:
                continue

            # tenant protection

            if (
                variant.product.tenant_id
                != current_user.tenant_id
            ):
                continue

            db.session.add(
                PriceListItem(

                    price_list_id=
                        price_list.id,

                    product_variant_id=
                        variant_id,

                    price=float(
                        value
                    )

                )
            )

            added += 1

        db.session.commit()

        flash(
            f"Price list updated ({added} items)",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        flash(
            str(e),
            "error"
        )

        return redirect(
            url_for(
                "pricing.edit_price_list",
                price_list_id=price_list.id
            )
        )

    return redirect(
        url_for(
            "pricing.view_price_list",
            price_list_id=price_list.id
        )
    )


# =========================================================
# DELETE PRICE LIST
# =========================================================
@pricing_bp.route("/price-lists/<int:price_list_id>/delete", methods=["POST"])
@login_required
def delete_price_list(price_list_id):

    price_list = PriceList.query.filter_by(
        id=price_list_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    PriceListItem.query.filter_by(
        price_list_id=price_list.id
    ).delete()

    db.session.delete(price_list)
    db.session.commit()

    flash("Price list deleted", "success")

    return redirect(url_for("pricing.list_price_lists"))