from app.core.models.base import BaseModel

from app.extensions import db
class LedgerEntry(BaseModel):
    __tablename__ = "ledger_entries"

    type = db.Column(db.String)  # sale, purchase, expense

    amount = db.Column(db.Float)

    currency = db.Column(db.String(10))

    reference_type = db.Column(db.String)
    reference_id = db.Column(db.Integer)