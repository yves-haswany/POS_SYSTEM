from app.extensions import db
from app.modules.inventory.models import Inventory
from app.modules.products.models import Product


def initialize_inventory_for_warehouse(warehouse):
    """
    Create inventory rows for ALL products of the warehouse's brand
    """

    products = Product.query.filter_by(
        brand_id=warehouse.brand_id
    ).all()

    for product in products:

        exists = Inventory.query.filter_by(
            product_id=product.id,
            warehouse_id=warehouse.id
        ).first()

        if not exists:
            db.session.add(Inventory(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity=0
            ))