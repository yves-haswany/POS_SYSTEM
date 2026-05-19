from app.extensions import db
from app.core.models.base import BaseModel


class Color(BaseModel):
    __tablename__ = "colors"

    name = db.Column(db.String(100), nullable=False)

    hex_code = db.Column(db.String(20))

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False
    )
    tenant = db.relationship("Tenant", backref="colors")

    def __repr__(self):
        return f"<Color {self.name}>"