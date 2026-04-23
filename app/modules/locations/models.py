from app.extensions import db
from app.core.models.base import BaseModel

class Location(BaseModel):
    __tablename__ = "locations"

    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String)

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))

    # ✅ MUST EXIST (this is what is missing in your project)
    tenant = db.relationship("Tenant", back_populates="locations")