from app.core import db
class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)

    brand_id = db.Column(db.Integer, db.ForeignKey("brand.id"))

    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"))