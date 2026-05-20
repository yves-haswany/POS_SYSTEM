from app.modules.style.models import Style
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db

styles_bp = Blueprint("styles", __name__, url_prefix="/styles")


@styles_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_style():

    if request.method == "POST":

        name = request.form.get("name")

        if not name:
            return "Name required", 400

        style = Style(
            name=name.strip(),
            tenant_id=current_user.tenant_id
        )

        db.session.add(style)
        db.session.commit()

        return redirect(url_for("style.create_style"))

    styles = Style.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(
        "style/create.html",
        styles=styles
    )