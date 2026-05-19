from app.extensions import db
from app.core.models.base import BaseModel
class Company(BaseModel):
    __tablename__ = 'companies'

    name = db.Column(db.String(100), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    tenant = db.relationship('Tenant', back_populates='companies')
    brands = db.relationship('Brand', back_populates='company', cascade='all, delete-orphan')
    
    