from flask import Blueprint, request, jsonify
from app.modules.orders.service import create_order

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/", methods=["POST"])
def create_order_route():
    data = request.json

    order = create_order(
        tenant_id=data["tenant_id"],
        location_id=data["location_id"],
        items=data["items"]
    )

    return jsonify({"id": order.id})