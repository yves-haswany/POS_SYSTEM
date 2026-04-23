from app.extensions import db
from app.modules.inventory.models import Inventory
from app.modules.stock_movements.models import StockMovement


def update_inventory(product_id, location_id, delta):
    inv = Inventory.query.filter_by(
        product_id=product_id,
        location_id=location_id
    ).first()

    if not inv:
        inv = Inventory(product_id=product_id, location_id=location_id, quantity=0)
        db.session.add(inv)

    inv.quantity += delta


def create_movement(product_id, from_loc, to_loc, quantity, type):
    movement = StockMovement(
        product_id=product_id,
        from_location_id=from_loc,
        to_location_id=to_loc,
        quantity=quantity,
        type=type
    )

    db.session.add(movement)

    # Apply stock changes
    if from_loc:
        update_inventory(product_id, from_loc, -quantity)

    if to_loc:
        update_inventory(product_id, to_loc, quantity)

    db.session.commit()

    return movement