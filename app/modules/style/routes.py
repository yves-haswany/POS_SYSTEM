from app.modules.products.models import Line
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db

lines_bp = Blueprint("lines", __name__, url_prefix="/lines")


@lines_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_line():

    if request.method == "POST":

        name = request.form.get("name")

        if not name:
            return "Name required", 400

        line = Line(
            name=name.strip(),
            tenant_id=current_user.tenant_id
        )

        db.session.add(line)
        db.session.commit()

        return redirect(url_for("lines.create_line"))

    lines = Line.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(
        "lines/create.html",
        lines=lines
    )