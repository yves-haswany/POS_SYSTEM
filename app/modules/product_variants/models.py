from app.extensions import db
from app.core.models.base import BaseModel


class ProductVariant(BaseModel):
    __tablename__ = "product_variants"

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    size_scale_id = db.Column(
        db.Integer,
        db.ForeignKey("size_scales.id"),
        nullable=True
    )
    barcode = db.Column(db.String(100), unique=True, index=True)
    color_id = db.Column(
        db.Integer,
        db.ForeignKey("colors.id"),
        nullable=True
    )

    sku = db.Column(db.String(100), unique=True)

    quantity = db.Column(db.Integer, default=0)

    price = db.Column(db.Float, default=0)

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    product = db.relationship("Product")
    color = db.relationship("Color")
    size_scale = db.relationship("SizeScale")
    size_id = db.Column(db.Integer, db.ForeignKey("size_scale_items.id"), nullable=True)
    size = db.relationship("SizeScaleItem")