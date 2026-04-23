from app.extensions import db
from app.core.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"

    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)