
from app.core.models.base import BaseModel

from app import db
class Style(BaseModel):
    __tablename__ = "styles"

    name = db.Column(db.String, nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)

    line_id = db.Column(db.Integer, db.ForeignKey("lines.id"))
    line = db.relationship("Line", backref="styles")

    tenant = db.relationship("Tenant", backref="styles")