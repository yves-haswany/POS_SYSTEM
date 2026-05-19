from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from app.modules.users.models import User
from app.core.services.user_service import create_user

auth_bp = Blueprint("auth", __name__)


# =====================================================
# 🔁 CENTRAL ROLE REDIRECT (FIXED)
# =====================================================
def redirect_by_role(user):
    role = (user.role or "").strip().lower()

    if role == "admin":
        return redirect(url_for("admin.dashboard"))

    elif role == "tenant":
        return redirect(url_for("tenant.dashboard"))

    elif role in ["branch_admin", "branch_manager", "vendor"]:
        return redirect(url_for("branch.dashboard"))

    return redirect(url_for("auth.login"))


# =====================================================
# LOGIN
# =====================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # 🔥 already logged in → go to correct dashboard
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Missing credentials", "error")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login"))

        # ✅ LOGIN
        login_user(user, remember=True)

        # 🔥 CRITICAL: redirect by role (NOT to "/")
        return redirect_by_role(user)

    return render_template("auth/login.html")


# =====================================================
# LOGOUT
# =====================================================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# =====================================================
# REGISTER
# =====================================================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if not username or not password:
            flash("Missing fields", "error")
            return redirect(url_for("auth.register"))

        create_user(username, password, role)

        flash("Account created successfully", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")