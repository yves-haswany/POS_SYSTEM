from app.extensions import db
from app.core.models.base import BaseModel

class Tenant(BaseModel):
    __tablename__ = "tenants"

    name = db.Column(db.String, nullable=False)

    integration_type = db.Column(db.String, default="none")
    integration_config = db.Column(db.JSON, default=dict)  # ✅ FIXED

    # 🔗 relationships
    users = db.relationship(
        "User",
        back_populates="tenant",
        cascade="all, delete"
    )

    locations = db.relationship(
        "Location",
        back_populates="tenant",
        cascade="all, delete"
    )