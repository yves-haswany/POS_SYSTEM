from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.modules.locations.models import Location
from app.modules.products.models import Product

tenant_bp = Blueprint("tenant", __name__)

@tenant_bp.route("/dashboard")
@login_required
def dashboard():
    # ✅ get tenant-specific data
    branches = Location.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    products = Product.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(
        "tenant/dashboard.html",
        branches=branches,
        products=products
    )