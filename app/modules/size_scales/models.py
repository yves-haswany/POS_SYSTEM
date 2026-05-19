from app.extensions import db
from app.core.models.base import BaseModel


class SizeScale(BaseModel):
    __tablename__ = "size_scales"

    name = db.Column(db.String(120), nullable=False)

    category = db.Column(db.String(120))

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    is_active = db.Column(db.Boolean, default=True)

    tenant = db.relationship(
        "Tenant",
        backref="size_scales"
    )
class SizeScaleItem(BaseModel):
    __tablename__ = "size_scale_items"

    size_scale_id = db.Column(
        db.Integer,
        db.ForeignKey("size_scales.id"),
        nullable=False
    )

    value = db.Column(db.String(50), nullable=False)

    sort_order = db.Column(db.Integer, default=0)

    size_scale = db.relationship(
        "SizeScale",
        backref="items"
    )