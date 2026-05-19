from app.extensions import db
from app.core.models.base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    # =========================
    # 🔹 Core Identity
    # =========================
    name = db.Column(db.String, nullable=False)
    sku = db.Column(db.String, unique=True, nullable=False)

    # =========================
    # 🔹 Classification
    # =========================
    season = db.Column(db.Enum("summer", "spring", "autumn", "winter", name="season_enum"))
    year = db.Column(db.Integer)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    category = db.relationship("Category", backref="products")

    segment = db.Column(db.String)
    line = db.Column(db.String)
    type = db.Column(db.String)

    composition = db.Column(db.Text)

    # =========================
    # 🔹 Pricing (base fallback only)
    # =========================
    price = db.Column(db.Float, nullable=True)

    purchase_currency = db.Column(db.String(10))
    cost = db.Column(db.Float)
    landing_cost = db.Column(db.Float)
    average_cost = db.Column(db.Float)

    vat_taxable = db.Column(db.Boolean, default=True)

    # =========================
    # 🔹 Inventory flags
    # =========================
    is_inventory_item = db.Column(db.Boolean, default=True)
    has_size = db.Column(
    db.Boolean,
    default=False
)

    has_color = db.Column(
    db.Boolean,
    default=False
)

    # =========================
    # 🔹 Status / Ownership
    # =========================
    is_active = db.Column(db.Boolean, default=True)
    is_draft = db.Column(
    db.Boolean,
    default=False
)

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)

    tenant = db.relationship("Tenant", back_populates="products")
    brand = db.relationship("Brand", backref="products")

    size_scale_id = db.Column(db.Integer, db.ForeignKey("size_scales.id"))
    size_scale = db.relationship("SizeScale")