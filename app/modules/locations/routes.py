from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.modules.locations.models import Location

locations_bp = Blueprint("locations", __name__)

# =========================================================
# 🔹 API ROUTES (JSON)
# =========================================================

# Create location (API)
@locations_bp.route("/", methods=["POST"])
@login_required
def create_location_api():
    data = request.json

    location = Location(
        name=data["name"],
        type=data["type"],  # store / warehouse
        tenant_id=current_user.tenant_id  # ✅ secure
    )

    db.session.add(location)
    db.session.commit()

    return jsonify({"id": location.id})


# List locations (API)
@locations_bp.route("/", methods=["GET"])
@login_required
def list_locations_api():
    locations = Location.query.filter_by(
        tenant_id=current_user.tenant_id  # ✅ tenant isolation
    ).all()

    return jsonify([
        {
            "id": l.id,
            "name": l.name,
            "type": l.type
        }
        for l in locations
    ])


# =========================================================
# 🔹 HTML ROUTES (UI)
# =========================================================

# Create location (form page)
@locations_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_location_page():
    if request.method == "POST":
        name = request.form.get("name")
        type_ = request.form.get("type")

        location = Location(
            name=name,
            type=type_,
            tenant_id=current_user.tenant_id
        )

        db.session.add(location)
        db.session.commit()

        return redirect(url_for("tenant.dashboard"))

    return render_template("locations/create.html")


# List locations (HTML page)
@locations_bp.route("/list")
@login_required
def list_locations_page():
    locations = Location.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()

    return render_template("locations/list.html", locations=locations)


# =========================================================
# 🔹 OPTIONAL: DELETE LOCATION
# =========================================================

@locations_bp.route("/delete/<int:location_id>", methods=["POST"])
@login_required
def delete_location(location_id):
    location = Location.query.filter_by(
        id=location_id,
        tenant_id=current_user.tenant_id  # 🔒 protect tenant
    ).first_or_404()

    db.session.delete(location)
    db.session.commit()

    return redirect(url_for("locations.list_locations_page"))