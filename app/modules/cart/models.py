
from app.core.models.base import BaseModel

from app.extensions import db
class Cart(BaseModel):
    __tablename__ = "carts"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"))

    status = db.Column(db.String, default="active")  # active / checked_out

class CartItem(BaseModel):
    __tablename__ = "cart_items"

    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"))
    product_variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"))

    quantity = db.Column(db.Integer, nullable=False)

    unit_price = db.Column(db.Float)
    currency = db.Column(db.String(10))