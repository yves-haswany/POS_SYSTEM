from app.extensions import db
from app.core.models.base import BaseModel
from flask_login import UserMixin


class User(BaseModel, UserMixin):
    __tablename__ = "users"

    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String(50), nullable=False)

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True)

    tenant = db.relationship("Tenant", back_populates="users")
    branch = db.relationship("Branch", back_populates="users")