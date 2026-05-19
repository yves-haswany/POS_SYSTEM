from app.extensions import db
from app.modules.inventory.models import Inventory
from app.modules.warehouses.models import Warehouse


def transfer_stock(product_id, from_warehouse_id, to_warehouse_id, quantity):

    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    source_wh = Warehouse.query.get(from_warehouse_id)
    dest_wh = Warehouse.query.get(to_warehouse_id)

    # 🔥 enforce same brand
    if source_wh.brand_id != dest_wh.brand_id:
        raise Exception("Cross-brand transfer not allowed")

    source = Inventory.query.filter_by(
        product_id=product_id,
        warehouse_id=from_warehouse_id
    ).first()

    destination = Inventory.query.filter_by(
        product_id=product_id,
        warehouse_id=to_warehouse_id
    ).first()

    if not source or not destination:
        raise Exception("Inventory record missing")

    if source.quantity < quantity:
        raise Exception("Not enough stock")

    source.quantity -= quantity
    destination.quantity += quantity

    db.session.flush()

    return True