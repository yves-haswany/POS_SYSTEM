from app.extensions import db
from app.core.models.base import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id")
    )

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("branches.id")
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    total = db.Column(
        db.Float,
        default=0
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by]
    )
    items = db.relationship(
        "OrderItem",
        backref="order",
        cascade="all, delete-orphan"
    )
class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")