from app.extensions import db
from app.modules.stock_movements.models import StockMovement
from app.modules.stock_reservations.service import StockReservationService


class StockMovementService:

    @staticmethod
    def create_stock_movement(
        tenant_id,
        product_variant_id,
        warehouse_id,
        quantity,
        movement_type,
        reference=None,
        notes=None,
        created_by=None,
        from_warehouse_id=None,
        to_warehouse_id=None
    ):

        # 🔒 VALIDATION (IMPORTANT)
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        if movement_type not in ["IN", "OUT", "TRANSFER"]:
            raise ValueError("Invalid movement type")

        # 🔥 CREATE MOVEMENT
        movement = StockMovement(
            tenant_id=tenant_id,
            product_variant_id=product_variant_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
            movement_type=movement_type,
            reference=reference,
            notes=notes,
            created_by=created_by,
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id
        )

        db.session.add(movement)

        return movement