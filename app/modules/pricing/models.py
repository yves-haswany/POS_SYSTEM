from app import db
from app.core.models.base import BaseModel
class PriceList(BaseModel):
    __tablename__ = "price_lists"

    name = db.Column(db.String, nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    currency = db.Column(db.String(10), nullable=False)

    items = db.relationship(
        "PriceListItem",
        backref="price_list",
        cascade="all, delete-orphan"
    )


class PriceListItem(BaseModel):
    __tablename__ = "price_list_items"

    price_list_id = db.Column(db.Integer, db.ForeignKey("price_lists.id"))
    product_variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"))

    price = db.Column(db.Float)