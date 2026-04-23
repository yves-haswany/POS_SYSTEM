from app.extensions import db
from app.core.models.base import BaseModel

class Inventory(BaseModel):
    __tablename__ = "inventory"

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))

    quantity = db.Column(db.Float, default=0)