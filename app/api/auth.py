from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.core.models.user import User
from app.extensions import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)

            # Redirect based on role
            if user.role == "admin":
                return redirect("/admin/dashboard")

            elif user.role == "tenant":
                return redirect("/tenant/dashboard")

            elif user.role == "branch":
                return redirect("/branch/pos")

        return "Invalid credentials"

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")