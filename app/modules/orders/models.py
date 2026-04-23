from app.extensions import db
from app.core.models.base import BaseModel

class Order(BaseModel):
    __tablename__ = "orders"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))

    total = db.Column(db.Float)