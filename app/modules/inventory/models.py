from app.extensions import db
from app.core.models.base import BaseModel

class Inventory(BaseModel):
    __tablename__ = "inventory"

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)

    quantity = db.Column(db.Float, default=0)

    product = db.relationship("Product")
    warehouse = db.relationship("Warehouse", back_populates="inventory")