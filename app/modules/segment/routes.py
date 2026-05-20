from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.modules.segment.models import Segment

segments_bp = Blueprint("segments", __name__, url_prefix="/segments")


@segments_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_segment():

    if request.method == "POST":

        name = request.form.get("name")

        if not name:
            return "Name required", 400

        segment = Segment(
            name=name.strip(),
            tenant_id=current_user.tenant_id
        )

        db.session.add(segment)
        db.session.commit()

        return redirect(url_for("segment.create_segment"))

    segments = Segment.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template(
        "segment/create.html",
        segments=segments
    )