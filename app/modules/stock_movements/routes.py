from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from app.modules.stock_movements.models import StockMovement

movements_bp = Blueprint(
    "movements",
    __name__,
    url_prefix="/stock-movements"
)


@movements_bp.route("/", methods=["GET"])
@login_required
def list_movements():

    movements = StockMovement.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(
        StockMovement.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": m.id,
            "product_id": m.product_id,
            "warehouse_id": m.warehouse_id,
            "quantity": m.quantity,
            "movement_type": m.movement_type,
            "reference": m.reference,
            "created_by": m.created_by,
            "created_at": m.created_at
        }
        for m in movements
    ])