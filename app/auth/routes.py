from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import app

from app.core.models.user import User
from app.core.services.user_service import create_user
from app.auth.utils import redirect_by_role   # ✅ moved here safely

auth_bp = Blueprint("auth", __name__)


# 🔐 LOGIN
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.login"))  #

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect_by_role(user)

        flash("Invalid username or password")

    return render_template("auth/login.html")


# 🚪 LOGOUT
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# 📝 REGISTER
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")

    create_user(username, password, role)

    return redirect(url_for("auth.login"))
