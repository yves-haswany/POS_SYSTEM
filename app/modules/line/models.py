
from app.core.models.base import BaseModel

from app import db
class Line(BaseModel):
    __tablename__ = "lines"

    name = db.Column(db.String, nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    tenant = db.relationship("Tenant", backref="lines")