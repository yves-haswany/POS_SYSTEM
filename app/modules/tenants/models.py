from app.extensions import db
from app.core.models.base import BaseModel

class Tenant(BaseModel):
    __tablename__ = "tenants"

    name = db.Column(db.String, nullable=False)

    integration_type = db.Column(db.String, default="none")
    integration_config = db.Column(db.JSON, default=dict)
    companies = db.relationship("Company", back_populates="tenant", cascade="all, delete-orphan")
    users = db.relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    brands = db.relationship("Brand", back_populates="tenant", cascade="all, delete-orphan")
    products = db.relationship("Product", back_populates="tenant", cascade="all, delete-orphan")