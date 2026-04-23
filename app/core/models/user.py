from app.extensions import db
from app.core.models.base import BaseModel
from flask_login import UserMixin

class User(BaseModel, UserMixin):
    __tablename__ = "users"

    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    role = db.Column(db.String(50), nullable=False)  # admin / tenant / branch

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=True)

    # 🔗 relationships
    tenant = db.relationship(
        "Tenant",
        back_populates="users"
    )