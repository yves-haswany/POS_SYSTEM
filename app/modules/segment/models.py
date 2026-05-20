
from app.core.models.base import BaseModel

from app import db
class Segment(BaseModel):
    __tablename__ = "segments"

    name = db.Column(db.String, nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)

    tenant = db.relationship("Tenant", backref="segments")