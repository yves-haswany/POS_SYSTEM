from app.extensions import db
from app.core.models.base import BaseModel

class Transfer(BaseModel):
    __tablename__ = "transfers"

    from_location_id = db.Column(db.Integer)
    to_location_id = db.Column(db.Integer)

    status = db.Column(db.String, default="pending")