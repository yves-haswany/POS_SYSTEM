from app.extensions import db
from app.core.models.base import BaseModel

class StockMovement(BaseModel):
    __tablename__ = "stock_movements"

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))

    from_location_id = db.Column(db.Integer, nullable=True)
    to_location_id = db.Column(db.Integer, nullable=True)

    quantity = db.Column(db.Float, nullable=False)

    type = db.Column(db.String)  # sale, transfer, purchase, adjustment