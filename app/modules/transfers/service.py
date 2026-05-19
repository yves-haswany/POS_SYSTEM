from app.extensions import db
from app.modules.stock_movements.service import create_stock_movement


def execute_transfer(transfer, items):
    # Remove from source
    for item in items:
        create_stock_movement(
            product_id=item["product_id"],
            from_loc=transfer.from_location_id,
            to_loc=None,
            quantity=item["qty"],
            type="transfer_out"
        )

    # Add to destination
    for item in items:
        create_stock_movement(
            product_id=item["product_id"],
            from_loc=None,
            to_loc=transfer.to_location_id,
            quantity=item["qty"],
            type="transfer_in"
        )

    transfer.status = "completed"
    db.session.commit()