from app.extensions import db
from app.core.models.base import BaseModel

class Brand(BaseModel):
    __tablename__ = "brands"

    name = db.Column(db.String(100), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)

    tenant = db.relationship("Tenant", back_populates="brands")
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    company = db.relationship("Company", back_populates="brands")

    branches = db.relationship(
        "Branch",
        back_populates="brand",
        cascade="all, delete-orphan"
    )

    # ✅ ALL WAREHOUSES (main + branch)
    warehouses = db.relationship(
        "Warehouse",
        back_populates="brand",
        cascade="all, delete-orphan"
    )

    # optional helper (NOT SQLAlchemy relation)
    @property
    def main_warehouse(self):
        return next((w for w in self.warehouses if w.branch_id is None), None)