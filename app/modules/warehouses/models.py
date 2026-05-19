from app.extensions import db
from app.core.models.base import BaseModel


class Warehouse(BaseModel):
    __tablename__ = "warehouses"

    name = db.Column(db.String(100), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)

    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True)

    parent_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True)

    # ✅ MUST MATCH Brand.warehouses
    brand = db.relationship(
        "Brand",
        back_populates="warehouses"
    )

    branch = db.relationship(
        "Branch",
        back_populates="warehouse",
        uselist=False
    )

    parent = db.relationship(
        "Warehouse",
        remote_side="Warehouse.id",
        backref="children"
    )

    inventory = db.relationship(
        "Inventory",
        back_populates="warehouse",
        cascade="all, delete-orphan"
    )