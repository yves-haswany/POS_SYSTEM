from app.extensions import db
from app.modules.orders.models import Order
from app.modules.stock_movements.service import create_movement


def create_order(tenant_id, location_id, items):
    total = sum(i["price"] * i["qty"] for i in items)

    order = Order(
        tenant_id=tenant_id,
        location_id=location_id,
        total=total
    )

    db.session.add(order)

    # Reduce stock
    for item in items:
        create_movement(
            product_id=item["product_id"],
            from_loc=location_id,
            to_loc=None,
            quantity=item["qty"],
            type="sale"
        )

    db.session.commit()

    return order