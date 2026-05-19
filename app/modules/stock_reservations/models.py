from app.extensions import db
from app.core.models.base import BaseModel


class StockReservation(BaseModel):
    __tablename__ = "stock_reservations"

    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False)

    product_variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=False)

    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String, default="reserved")
    # reserved / confirmed / released / expired

    expires_at = db.Column(db.DateTime)