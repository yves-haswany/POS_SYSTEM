from app.core.models.base import BaseModel
from app.extensions import db
class CurrencyRate(BaseModel):
    __tablename__ = "currency_rates"

    from_currency = db.Column(db.String(10))
    to_currency = db.Column(db.String(10))

    rate = db.Column(db.Float)

    date = db.Column(db.Date)