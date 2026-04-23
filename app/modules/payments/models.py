from app.extensions import db
from app.core.models.base import BaseModel

class Payment(BaseModel):
    __tablename__ = "payments"

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    amount = db.Column(db.Float)
    method = db.Column(db.String)  # cash/card