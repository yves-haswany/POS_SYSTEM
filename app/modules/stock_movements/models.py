from app.extensions import db
from app.core.models.base import BaseModel


class StockMovement(BaseModel):
    __tablename__ = "stock_movements"

    tenant_id = db.Column(db.Integer, nullable=False)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    # 🟡 The warehouse this movement affects (main ledger anchor)
    warehouse_id = db.Column(
        db.Integer,
        db.ForeignKey("warehouses.id"),
        nullable=False
    )

    # 🟢 Transfer support (optional but powerful)
    from_warehouse_id = db.Column(
        db.Integer,
        db.ForeignKey("warehouses.id"),
        nullable=True
    )

    to_warehouse_id = db.Column(
        db.Integer,
        db.ForeignKey("warehouses.id"),
        nullable=True
    )

    quantity = db.Column(db.Float, nullable=False)

    movement_type = db.Column(db.String, nullable=False)
    # sale
    # purchase
    # transfer_out
    # transfer_in
    # adjustment
    # return
    # wastage

    reference = db.Column(db.String, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # Relationships
    product = db.relationship("Product", foreign_keys=[product_id])
    warehouse = db.relationship("Warehouse", foreign_keys=[warehouse_id])

    from_warehouse = db.relationship(
        "Warehouse",
        foreign_keys=[from_warehouse_id]
    )

    to_warehouse = db.relationship(
        "Warehouse",
        foreign_keys=[to_warehouse_id]
    )