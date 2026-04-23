from flask import Blueprint, jsonify
from app.modules.inventory.models import Inventory

inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.route("/", methods=["GET"])
def list_inventory():
    items = Inventory.query.all()

    return jsonify([
        {
            "product_id": i.product_id,
            "location_id": i.location_id,
            "quantity": i.quantity
        }
        for i in items
    ])