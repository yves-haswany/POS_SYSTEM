from flask import Blueprint, jsonify
from app.modules.stock_movements.models import StockMovement

movements_bp = Blueprint("movements", __name__)

@movements_bp.route("/", methods=["GET"])
def list_movements():
    movements = StockMovement.query.all()

    return jsonify([
        {
            "id": m.id,
            "product_id": m.product_id,
            "from": m.from_location_id,
            "to": m.to_location_id,
            "qty": m.quantity,
            "type": m.type
        }
        for m in movements
    ])