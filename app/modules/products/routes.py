from flask import Blueprint, request, jsonify
from app.extensions import db
from app.modules.products.models import Product
from flask_login import current_user, login_required

products_bp = Blueprint("products", __name__)

@products_bp.route("/", methods=["POST"])
@login_required
def create_product():
    data = request.json

    product = Product(
        name=data["name"],
        price=data["price"],
        tenant_id=current_user.tenant_id
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({"id": product.id})