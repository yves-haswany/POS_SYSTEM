from flask import Blueprint, render_template, url_for, request, redirect, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.modules.tenants.models import Tenant
from app.modules.users.models import User
from app.modules.companies.models import Company
from app.modules.brands.models import Brand
from app.modules.branches.models import Branch

from app.services.warehouse_service import (
    create_brand_main_warehouse,
    create_branch_warehouse
)
from app.services.inventory_service import (
    initialize_inventory_for_warehouse
)

admin_bp = Blueprint("admin", __name__)


# =====================================================
# 🔒 ADMIN GUARD
# =====================================================
def require_admin():
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)


# =====================================================
# DASHBOARD
# =====================================================
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    require_admin()
    tenants = Tenant.query.all()
    return render_template("admin/dashboard.html", tenants=tenants)


# =====================================================
# CREATE TENANT (WITH BRANCH POS ADMINS)
# =====================================================
@admin_bp.route("/create-tenant", methods=["GET", "POST"])
@login_required
def create_tenant():
    require_admin()

    if request.method == "POST":

        try:

            # =====================================================
            # BASIC FIELDS
            # =====================================================

            name = request.form.get("name", "").strip()
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            company_names = request.form.getlist("company_name[]")

            brand_names = request.form.getlist("brand_name[]")
            brand_company_indexes = request.form.getlist("brand_company_index[]")

            branch_names = request.form.getlist("branch_name[]")
            branch_brand_indexes = request.form.getlist("branch_brand_index[]")

            branch_admin_usernames = request.form.getlist("branch_admin_username[]")
            branch_admin_passwords = request.form.getlist("branch_admin_password[]")

            # =====================================================
            # VALIDATION
            # =====================================================

            if not name or not username or not password:
                flash("Tenant credentials are required", "error")
                return redirect(url_for("admin.create_tenant"))

            # UNIQUE TENANT NAME
            existing_tenant = Tenant.query.filter_by(name=name).first()

            if existing_tenant:
                flash("Tenant name already exists", "error")
                return redirect(url_for("admin.create_tenant"))

            # UNIQUE TENANT ADMIN USERNAME
            existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                flash("Tenant admin username already exists", "error")
                return redirect(url_for("admin.create_tenant"))

            # UNIQUE BRANCH ADMIN USERNAMES
            for branch_username in branch_admin_usernames:

                if not branch_username:
                    continue

                exists = User.query.filter_by(
                    username=branch_username.strip()
                ).first()

                if exists:
                    flash(
                        f"Branch admin username '{branch_username}' already exists",
                        "error"
                    )
                    return redirect(url_for("admin.create_tenant"))

            # =====================================================
            # CREATE TENANT
            # =====================================================

            tenant = Tenant(name=name)

            db.session.add(tenant)
            db.session.flush()

            # =====================================================
            # CREATE TENANT ADMIN
            # =====================================================

            tenant_user = User(
                username=username,
                password=generate_password_hash(password),
                role="tenant",
                tenant_id=tenant.id
            )

            db.session.add(tenant_user)

            # =====================================================
            # CREATE COMPANIES
            # =====================================================

            companies = []

            for c_name in company_names:

                c_name = c_name.strip()

                if not c_name:
                    continue

                company = Company(
                    name=c_name,
                    tenant_id=tenant.id
                )

                db.session.add(company)
                db.session.flush()

                companies.append(company)

            # DEFAULT COMPANY
            if not companies:

                default_company = Company(
                    name=f"{name} Company",
                    tenant_id=tenant.id
                )

                db.session.add(default_company)
                db.session.flush()

                companies.append(default_company)

            # =====================================================
            # CREATE BRANDS
            # =====================================================

            brands = []

            for i, b_name in enumerate(brand_names):

                b_name = b_name.strip()

                if not b_name:
                    continue

                # SAFE COMPANY INDEX
                try:
                    company_index = int(brand_company_indexes[i])
                    company = companies[company_index]

                except Exception:
                    company = companies[0]

                brand = Brand(
                    name=b_name,
                    tenant_id=tenant.id,
                    company_id=company.id
                )

                db.session.add(brand)
                db.session.flush()

                # =================================================
                # CREATE MAIN WAREHOUSE
                # =================================================

                warehouse = create_brand_main_warehouse(brand)

                if warehouse:
                    initialize_inventory_for_warehouse(warehouse)

                brands.append(brand)

            # DEFAULT BRAND
            if not brands:

                default_brand = Brand(
                    name=f"{name} Default Brand",
                    tenant_id=tenant.id,
                    company_id=companies[0].id
                )

                db.session.add(default_brand)
                db.session.flush()

                warehouse = create_brand_main_warehouse(default_brand)

                if warehouse:
                    initialize_inventory_for_warehouse(warehouse)

                brands.append(default_brand)

            # =====================================================
            # CREATE BRANCHES
            # =====================================================

            max_len = max(
                len(branch_names or []),
                len(branch_brand_indexes or []),
                len(branch_admin_usernames or []),
                len(branch_admin_passwords or [])
            )

            for i in range(max_len):

                b_name = (
                    branch_names[i].strip()
                    if i < len(branch_names)
                    else None
                )

                b_index = (
                    branch_brand_indexes[i]
                    if i < len(branch_brand_indexes)
                    else "0"
                )

                b_user = (
                    branch_admin_usernames[i].strip()
                    if i < len(branch_admin_usernames)
                    else None
                )

                b_pass = (
                    branch_admin_passwords[i].strip()
                    if i < len(branch_admin_passwords)
                    else None
                )

                if not b_name:
                    continue

                # SAFE BRAND INDEX
                try:
                    brand = brands[int(b_index)]

                except Exception:
                    brand = brands[0]

                # =================================================
                # CREATE BRANCH
                # =================================================

                branch = Branch(
                    name=b_name,
                    tenant_id=tenant.id,
                    brand_id=brand.id
                )

                db.session.add(branch)
                db.session.flush()

                # =================================================
                # CREATE BRANCH WAREHOUSE
                # =================================================

                create_branch_warehouse(branch)

                # =================================================
                # CREATE BRANCH ADMIN
                # =================================================

                if b_user and b_pass:

                    branch_user = User(
                        username=b_user,
                        password=generate_password_hash(b_pass),
                        role="branch_admin",
                        tenant_id=tenant.id,
                        branch_id=branch.id
                    )

                    db.session.add(branch_user)

            # =====================================================
            # COMMIT
            # =====================================================

            db.session.commit()

            flash("Tenant created successfully", "success")

            return redirect(url_for("admin.dashboard"))

        except Exception as e:

            db.session.rollback()

            import traceback
            traceback.print_exc()

            print("ERROR:", str(e))

            flash(f"Error creating tenant: {str(e)}", "error")

            return redirect(url_for("admin.create_tenant"))

    return render_template("admin/create_tenant.html")


# =====================================================
# EDIT TENANT (FIXED + SAFE + POS ADMINS SUPPORTED)
# =====================================================
@admin_bp.route("/tenant/<int:tenant_id>/edit", methods=["GET", "POST"])
@login_required
def edit_tenant(tenant_id):
    require_admin()

    tenant = Tenant.query.get_or_404(tenant_id)

    companies = Company.query.filter_by(tenant_id=tenant.id).all()
    brands = Brand.query.filter_by(tenant_id=tenant.id).all()
    branches = Branch.query.filter_by(tenant_id=tenant.id).all()

    if request.method == "POST":
        try:
            branch_ids = request.form.getlist("branch_id[]")
            branch_names = request.form.getlist("branch_name[]")
            branch_brand_ids = request.form.getlist("branch_brand_id[]")
            branch_usernames = request.form.getlist("branch_username[]")
            branch_passwords = request.form.getlist("branch_password[]")

            max_len = len(branch_names)

            for i in range(max_len):
                b_id = branch_ids[i] if i < len(branch_ids) else None
                b_name = branch_names[i]
                b_brand_id = branch_brand_ids[i] if i < len(branch_brand_ids) else None
                b_user = branch_usernames[i] if i < len(branch_usernames) else None
                b_pass = branch_passwords[i] if i < len(branch_passwords) else None

                if not b_name:
                    continue

                brand = Brand.query.filter_by(
                    id=int(b_brand_id),
                    tenant_id=tenant.id
                ).first()

                if not brand:
                    continue

                # -------------------------
                # UPDATE
                # -------------------------
                if b_id:
                    branch = Branch.query.get(int(b_id))
                    if not branch:
                        continue

                    branch.name = b_name
                    branch.brand_id = brand.id

                    user = User.query.filter_by(
                        branch_id=branch.id,
                        role="branch_admin"
                    ).first()

                    if user:
                        if b_user:
                            user.username = b_user
                        if b_pass:
                            user.password = generate_password_hash(b_pass)
                    else:
                        if b_user and b_pass:
                            db.session.add(User(
                                username=b_user,
                                password=generate_password_hash(b_pass),
                                role="branch_admin",
                                tenant_id=tenant.id,
                                branch_id=branch.id
                            ))

                # -------------------------
                # CREATE NEW
                # -------------------------
                else:
                    branch = Branch(
                        name=b_name,
                        tenant_id=tenant.id,
                        brand_id=brand.id
                    )
                    db.session.add(branch)
                    db.session.flush()

                    create_branch_warehouse(branch)

                    if b_user and b_pass:
                        db.session.add(User(
                            username=b_user,
                            password=generate_password_hash(b_pass),
                            role="branch_admin",
                            tenant_id=tenant.id,
                            branch_id=branch.id
                        ))

            db.session.commit()

            flash("Tenant updated successfully", "success")
            return redirect(url_for("admin.dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("admin.edit_tenant", tenant_id=tenant.id))

    return render_template(
        "admin/edit_tenant.html",
        tenant=tenant,
        companies=companies,
        brands=brands,
        branches=branches
    )
@admin_bp.route("/tenant/<int:tenant_id>/change-password", methods=["GET", "POST"])
@login_required
def change_tenant_password(tenant_id):
    require_admin()

    tenant = Tenant.query.get_or_404(tenant_id)

    user = User.query.filter_by(
        tenant_id=tenant.id,
        role="tenant"
    ).first()

    if not user:
        flash("Tenant admin not found", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":

        new_password = request.form.get("password", "").strip()

        if not new_password:
            flash("Password is required", "error")
            return redirect(url_for("admin.change_tenant_password", tenant_id=tenant_id))

        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Password updated successfully", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template(
        "admin/change_password.html",
        tenant=tenant,
        user=user
    )