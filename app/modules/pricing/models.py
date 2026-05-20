from app import db
from app.core.models.base import BaseModel


class PriceList(BaseModel):

    __tablename__ = "price_lists"

    name = db.Column(
        db.String,
        nullable=False
    )

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tenants.id"
        ),
        nullable=False
    )

    currency = db.Column(
        db.String(10),
        nullable=False
    )

    items = db.relationship(
        "PriceListItem",
        back_populates="price_list",
        cascade="all, delete-orphan"
    )


class PriceListItem(BaseModel):

    __tablename__ = "price_list_items"

    price_list_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "price_lists.id"
        ),
        nullable=False
    )

    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "product_variants.id"
        ),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    # relationship to parent list
    price_list = db.relationship(
        "PriceList",
        back_populates="items"
    )

    # relationship to variant
    product_variant = db.relationship(
        "ProductVariant",
        lazy="joined"
    )