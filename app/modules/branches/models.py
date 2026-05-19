from app.extensions import db
from app.core.models.base import BaseModel


class Branch(BaseModel):
    __tablename__ = "branches"

    name = db.Column(db.String(100), nullable=False)

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)

    brand = db.relationship("Brand", back_populates="branches")

    users = db.relationship("User", back_populates="branch")

    warehouse = db.relationship(
        "Warehouse",
        back_populates="branch",
        uselist=False
    )