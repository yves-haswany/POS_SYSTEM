from app import db
from app.modules.inventory_valuation.models import InventoryValuation
class InventoryValuationService:

    @staticmethod
    def update_average_cost(variant_id, new_qty, new_cost):

        record = InventoryValuation.query.filter_by(
            product_variant_id=variant_id
        ).first()

        if not record:
            record = InventoryValuation(
                product_variant_id=variant_id,
                quantity=new_qty,
                total_cost=new_qty * new_cost,
                average_cost=new_cost
            )
            db.session.add(record)
        else:
            old_qty = record.quantity
            old_avg = record.average_cost

            new_avg = ((old_qty * old_avg) + (new_qty * new_cost)) / (old_qty + new_qty)

            record.quantity += new_qty
            record.average_cost = new_avg
            record.total_cost = record.quantity * new_avg

        db.session.commit()
        return record