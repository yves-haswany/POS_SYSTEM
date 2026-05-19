from app.core.models.base import BaseModel

from app.extensions import db
class InventoryValuation(BaseModel):
    __tablename__ = "inventory_valuation"

    product_variant_id = db.Column(db.Integer)
    location_id = db.Column(db.Integer)

    quantity = db.Column(db.Float)

    total_cost = db.Column(db.Float)

    average_cost = db.Column(db.Float)