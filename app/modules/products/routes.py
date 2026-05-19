from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash
)
from sqlalchemy.orm import joinedload

from flask_login import current_user, login_required

import pandas as pd
import uuid
import traceback
import os

from werkzeug.utils import secure_filename

from app.extensions import db

from app.modules.products.models import Product
from app.modules.brands.models import Brand
from app.modules.warehouses.models import Warehouse
from app.modules.inventory.models import Inventory
from app.modules.categories.models import Category
from app.modules.product_variants.models import ProductVariant
from app.modules.size_scales.models import SizeScale

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/products"
)


# =========================================================
# CREATE PRODUCT
# =========================================================
# 
@products_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create_product():

    brands = Brand.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    categories = Category.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    size_scales = SizeScale.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    if request.method == "POST":

        try:

            has_size = (
                "has_size"
                in request.form
            )

            has_color = (
                "has_color"
                in request.form
            )

            has_variants = (
                has_size
                or
                has_color
            )

            product = Product(

                # identity
                name=request.form.get(
                    "name",
                    ""
                ).strip(),

                sku=request.form.get(
                    "sku",
                    ""
                ).strip(),

                season=request.form.get(
                    "season"
                ) or None,

                year=(
                    int(
                        request.form.get(
                            "year"
                        )
                    )

                    if request.form.get(
                        "year"
                    )

                    else None
                ),

                # classification
                category_id=(

                    int(
                        request.form.get(
                            "category_id"
                        )
                    )

                    if request.form.get(
                        "category_id"
                    )

                    else None
                ),

                segment=request.form.get(
                    "segment"
                ),

                line=request.form.get(
                    "line"
                ),

                type=request.form.get(
                    "type"
                ),

                composition=request.form.get(
                    "composition"
                ),

                # pricing
                price=float(

                    request.form.get(
                        "price",
                        0
                    ) or 0

                ),

                purchase_currency=request.form.get(
                    "purchase_currency"
                ),

                cost=float(

                    request.form.get(
                        "cost",
                        0
                    ) or 0

                ),

                landing_cost=float(

                    request.form.get(
                        "landing_cost",
                        0
                    ) or 0

                ),

                average_cost=float(

                    request.form.get(
                        "average_cost",
                        0
                    ) or 0

                ),

                vat_taxable=(

                    "vat_taxable"

                    in request.form

                ),

                # inventory
                is_inventory_item=(

                    "is_inventory_item"

                    in request.form

                ),

                has_size=has_size,

                has_color=has_color,

                size_scale_id=(

                    int(
                        request.form.get(
                            "size_scale_id"
                        )
                    )

                    if request.form.get(
                        "size_scale_id"
                    )

                    else None
                ),

                # ownership
                brand_id=int(
                    request.form.get(
                        "brand_id"
                    )
                ),

                tenant_id=current_user.tenant_id,

                # auto status
                is_draft=has_variants,

                is_active=(
                    not has_variants
                )

            )

            db.session.add(
                product
            )

            db.session.flush()

            quantity = int(

                request.form.get(
                    "quantity",
                    0
                ) or 0

            )

            if (

                not has_variants

                and

                quantity > 0

            ):

                warehouse = Warehouse.query.filter_by(

                    brand_id=product.brand_id,

                    branch_id=None

                ).first()

                if warehouse:

                    inventory = Inventory.query.filter_by(

                        warehouse_id=warehouse.id,

                        product_id=product.id

                    ).first()

                    if not inventory:

                        inventory = Inventory(

                            warehouse_id=warehouse.id,

                            product_id=product.id,

                            quantity=0

                        )

                        db.session.add(
                            inventory
                        )

                    inventory.quantity += quantity

            db.session.commit()

            if has_variants:

                return redirect(

                    url_for(

                        "product_variants.variant_matrix",

                        product_id=product.id

                    )

                )

            flash(
                "Product created",
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

        "products/create.html",

        brands=brands,

        categories=categories,

        size_scales=size_scales

    )


# =========================================================
# EDIT PRODUCT
# =========================================================
@products_bp.route(
    "/<int:product_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_product(product_id):

    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()

    variants = ProductVariant.query.options(

        joinedload(
            ProductVariant.size
        ),

        joinedload(
            ProductVariant.color
        )

    ).filter_by(

        product_id=product.id,

        tenant_id=current_user.tenant_id

    ).all()

    if request.method == "POST":

        try:

            # ==========================
            # PRODUCT
            # ==========================
            product.name = request.form.get(
                "name",
                ""
            ).strip()

            product.sku = request.form.get(
                "sku",
                ""
            ).strip()

            try:

                product.price = float(

                    request.form.get(
                        "price",
                        product.price or 0
                    )

                )

            except ValueError:

                return "Invalid price", 400

            brand_id = request.form.get(
                "brand_id"
            )

            if brand_id:

                brand = Brand.query.filter_by(

                    id=int(brand_id),

                    tenant_id=current_user.tenant_id

                ).first_or_404()

                product.brand_id = brand.id

            category_id = request.form.get(
                "category_id"
            )

            product.category_id = (

                int(category_id)

                if category_id

                else None

            )

            # ==========================
            # SIMPLE PRODUCT
            # ==========================
            if (

                not product.has_size

                and

                not product.has_color

            ):

                product.barcode = request.form.get(
                    "barcode",
                    product.barcode
                )

                try:

                    product.quantity = int(

                        request.form.get(
                            "quantity",
                            product.quantity or 0
                        )

                    )

                except ValueError:

                    product.quantity = 0

            # ==========================
            # VARIANTS
            # ==========================
            for variant in variants:

                variant.barcode = request.form.get(

                    f"barcode_{variant.id}",

                    variant.barcode

                )

                try:

                    variant.quantity = int(

                        request.form.get(

                            f"qty_{variant.id}",

                            variant.quantity

                        )

                    )

                except ValueError:

                    variant.quantity = variant.quantity

                try:

                    variant.price = float(

                        request.form.get(

                            f"price_{variant.id}",

                            variant.price

                        )

                    )

                except ValueError:

                    variant.price = variant.price

            db.session.commit()

            flash(
                "Product updated successfully",
                "success"
            )

            return redirect(
                url_for(
                    "tenant.dashboard"
                )
            )

        except Exception as e:

            db.session.rollback()

            return str(e), 500

    brands = Brand.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    categories = Category.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(

        "products/edit.html",

        product=product,

        brands=brands,

        categories=categories,

        variants=variants
    )
# =========================================================
# IMPORT PRODUCTS EXCEL
# =========================================================
@products_bp.route("/import-excel", methods=["POST"])
@login_required
def import_products_excel():

    try:

        file = request.files.get("file")

        if not file:
            return "No file uploaded", 400

        filename = secure_filename(file.filename)

        if not filename.endswith(".xlsx"):
            return "Only .xlsx files are allowed", 400

        # =================================================
        # READ EXCEL
        # =================================================
        df = pd.read_excel(file)

        required_cols = [
            "name",
            "price",
            "brand_id"
        ]

        for col in required_cols:

            if col not in df.columns:
                return f"Missing column: {col}", 400

        created_count = 0

        # =================================================
        # PROCESS ROWS
        # =================================================
        for _, row in df.iterrows():

            name = str(row["name"]).strip()

            price = float(row["price"])

            brand_id = int(row["brand_id"])

            sku = (
                str(row["sku"])
                if "sku" in row and not pd.isna(row["sku"])
                else None
            )

            quantity = (
                int(row["quantity"])
                if "quantity" in row
                and not pd.isna(row["quantity"])
                else 0
            )

            category_id = (
                int(row["category_id"])
                if "category_id" in row
                and not pd.isna(row["category_id"])
                else None
            )

            # AUTO SKU
            if not sku or sku == "nan":

                sku = (
                    f"SKU-"
                    f"{uuid.uuid4().hex[:8].upper()}"
                )

            # validate brand
            brand = Brand.query.filter_by(
                id=brand_id,
                tenant_id=current_user.tenant_id
            ).first()

            if not brand:
                continue

            # =================================================
            # CREATE PRODUCT
            # =================================================
            product = Product(
                name=name,
                price=price,
                sku=sku,

                brand_id=brand.id,

                category_id=category_id,

                tenant_id=current_user.tenant_id,

                has_size_and_color=False
            )

            db.session.add(product)

            db.session.flush()

            # =================================================
            # INVENTORY
            # =================================================
            if quantity > 0:

                warehouse = Warehouse.query.filter_by(
                    brand_id=brand.id,
                    branch_id=None
                ).first()

                if warehouse:

                    inventory = Inventory.query.filter_by(
                        warehouse_id=warehouse.id,
                        product_id=product.id
                    ).first()

                    if not inventory:

                        inventory = Inventory(
                            warehouse_id=warehouse.id,
                            product_id=product.id,
                            quantity=0
                        )

                        db.session.add(inventory)

                    inventory.quantity += quantity

            created_count += 1

        db.session.commit()

        return jsonify({
            "message": "Import successful",
            "created": created_count
        })

    except Exception as e:

        db.session.rollback()

        traceback.print_exc()

        return f"Error: {str(e)}", 500