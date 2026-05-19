from app.extensions import db
from app.core.models.base import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(120), nullable=False)

    # Optional hierarchy
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    parent = db.relationship(
        "Category",
        remote_side="Category.id",
        backref="children"
    )

    tenant = db.relationship(
        "Tenant",
        backref="categories"
    )

    def __repr__(self):
        return f"<Category {self.name}>"