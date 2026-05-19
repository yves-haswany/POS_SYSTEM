from flask import Blueprint, flash, render_template, url_for, redirect, abort, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.modules.products.models import Product
from app.modules.users.models import User
from app.modules.branches.models import Branch
from app.modules.brands.models import Brand
from app.modules.warehouses.models import Warehouse  # ✅ IMPORTANT

tenant_bp = Blueprint("tenant", __name__)


# =====================================================
# DASHBOARD
# =====================================================
from flask import Blueprint, render_template, url_for, redirect, abort, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.modules.products.models import Product
from app.modules.users.models import User
from app.modules.branches.models import Branch
from app.modules.brands.models import Brand  # ✅ IMPORTANT

tenant_bp = Blueprint("tenant", __name__)


# =====================================================
# DASHBOARD
# =====================================================
@tenant_bp.route("/dashboard")
@login_required
def dashboard():

    # 🔥 SAFE TENANT FILTER VIA BRAND
    branches = Branch.query.join(Brand).filter(
        Brand.tenant_id == current_user.tenant_id
    ).all()

    # 🔥 PRODUCTS BELONG TO BRAND → FILTER VIA BRAND
    products = Product.query.join(Brand).filter(
        Brand.tenant_id == current_user.tenant_id
    ).all()
    warehouses = Warehouse.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()
    return render_template(
        "tenant/dashboard.html",
        branches=branches,
        products=products,
        warehouses = warehouses
    )
@tenant_bp.route("/warehouses/create", methods=["GET", "POST"])
@login_required
def create_warehouse():

    if request.method == "POST":
        name = request.form.get("name")
        brand_id = int(request.form.get("brand_id"))
        branch_id = request.form.get("branch_id")

        # convert branch_id safely
        branch_id = int(branch_id) if branch_id else None

        brand = Brand.query.filter_by(
            id=brand_id,
            tenant_id=current_user.tenant_id
        ).first_or_404()

        # 🔥 if branch is selected → validate it belongs to tenant
        if branch_id:
            branch = Branch.query.filter_by(
                id=branch_id,
                tenant_id=current_user.tenant_id
            ).first_or_404()
        else:
            branch = None

        warehouse = Warehouse(
            name=name,
            tenant_id=current_user.tenant_id,
            brand_id=brand.id,
            branch_id=branch.id if branch else None
        )

        db.session.add(warehouse)
        db.session.commit()

        flash("Warehouse created", "success")
        return redirect(url_for("tenant.dashboard"))

    brands = Brand.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    branches = Branch.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(
        "tenant/create_warehouse.html",
        brands=brands,
        branches=branches
    )

# =====================================================
# EDIT BRANCH
# =====================================================
@tenant_bp.route("/warehouses/<int:warehouse_id>/edit", methods=["GET", "POST"])
@login_required
def edit_warehouse(warehouse_id):

    warehouse = Warehouse.query.get_or_404(warehouse_id)

    if warehouse.brand.tenant_id != current_user.tenant_id:
        abort(403)

    if request.method == "POST":
        warehouse.name = request.form.get("name")
        db.session.commit()
        return redirect(url_for("tenant.dashboard"))

    return render_template("tenant/edit_warehouse.html", warehouse=warehouse)


# =====================================================
# EDIT BRANCH
# =====================================================
@tenant_bp.route("/warehouses/<int:warehouse_id>/delete", methods=["POST"])
@login_required
def delete_warehouse(warehouse_id):

    warehouse = Warehouse.query.get_or_404(warehouse_id)

    if warehouse.brand.tenant_id != current_user.tenant_id:
        abort(403)

    db.session.delete(warehouse)
    db.session.commit()

    flash("Warehouse deleted", "success")
    return redirect(url_for("tenant.dashboard"))
