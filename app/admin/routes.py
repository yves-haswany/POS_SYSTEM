from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_required
from werkzeug.security import generate_password_hash
from app import db
from app.core.models.tenant import Tenant
from app.core.models.user import User
from app.modules.locations.models import Location
admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    tenants = Tenant.query.all()

    return render_template(
        "admin/dashboard.html",
        tenants=tenants
    )
@admin_bp.route("/create-tenant", methods=["GET", "POST"])
@login_required
def create_tenant():
    from flask import request, redirect, url_for, flash
    from app.extensions import db
    from app.core.models.tenant import Tenant
    from app.core.models.user import User
    from app.modules.locations.models import Location
    from werkzeug.security import generate_password_hash

    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")

        branch_names = request.form.getlist("branch_name[]")
        branch_types = request.form.getlist("branch_type[]")

        # =========================
        # 🔴 VALIDATION
        # =========================
        if not name or not username or not password:
            flash("All tenant fields are required")
            return redirect(url_for("admin.create_tenant"))

        if not branch_names or all(not b.strip() for b in branch_names):
            flash("At least one branch is required")
            return redirect(url_for("admin.create_tenant"))

        for i, (b_name, b_type) in enumerate(zip(branch_names, branch_types)):
            if b_name.strip() and not b_type:
                flash(f"Branch #{i+1} must have a type")
                return redirect(url_for("admin.create_tenant"))

        # =========================
        # ✅ CREATE TENANT
        # =========================
        tenant = Tenant(name=name)
        db.session.add(tenant)
        db.session.flush()  # get tenant.id

        # =========================
        # ✅ CREATE USER
        # =========================
        user = User(
            username=username,
            password=generate_password_hash(password),
            role="tenant",
            tenant_id=tenant.id
        )
        db.session.add(user)

        # =========================
        # ✅ CREATE BRANCHES
        # =========================
        for branch_name, branch_type in zip(branch_names, branch_types):
            if branch_name.strip():
                location = Location(
                    name=branch_name.strip(),
                    type=branch_type,
                    tenant_id=tenant.id
                )
                db.session.add(location)

        db.session.commit()

        flash("Tenant created successfully")
        return redirect(url_for("admin.create_tenant"))

    return render_template("admin/create_tenant.html")
@admin_bp.route("/tenant/<int:tenant_id>/change-password", methods=["GET", "POST"])
@login_required
def change_tenant_password(tenant_id):
    from app.extensions import db
    from app.core.models.user import User
    from werkzeug.security import generate_password_hash
    from flask import request, redirect, url_for, render_template, flash

    # get tenant admin user
    user = User.query.filter_by(
        tenant_id=tenant_id,
        role="tenant"
    ).first()

    if not user:
        flash("Tenant user not found", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        new_password = request.form.get("password")

        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Password updated successfully", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/change_password.html", user=user)
@admin_bp.route("/tenant/<int:tenant_id>/edit", methods=["GET", "POST"])
@login_required
def edit_tenant(tenant_id):
    from app.core.models.tenant import Tenant
    from app.modules.locations.models import Location
    from app.extensions import db

    tenant = Tenant.query.get_or_404(tenant_id)

    if request.method == "POST":
        branch_names = request.form.getlist("branches[]")

        for branch_name in branch_names:
            if branch_name.strip():
                location = Location(
                    name=branch_name,
                    type="branch",
                    tenant_id=tenant.id
                )
                db.session.add(location)

        db.session.commit()

        return redirect(url_for("admin.dashboard"))

    return render_template("admin/edit_tenant.html", tenant=tenant)
@admin_bp.route("/tenant/<int:tenant_id>/branches")
@login_required
def tenant_branches(tenant_id):
    from app.modules.locations.models import Location
    from app.core.models.tenant import Tenant

    tenant = Tenant.query.get_or_404(tenant_id)

    branches = Location.query.filter_by(tenant_id=tenant.id).all()

    return render_template(
        "admin/tenant_branches.html",
        tenant=tenant,
        branches=branches
    )