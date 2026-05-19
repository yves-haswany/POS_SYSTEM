from app.extensions import db
from app.core.models.base import BaseModel

class Transfer(db.Model):
    __tablename__ = "transfers"

    id = db.Column(db.Integer, primary_key=True)

    tenant_id = db.Column(db.Integer, nullable=False)

    source_warehouse_id = db.Column(db.Integer, nullable=False)
    destination_warehouse_id = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String, default="pending")  
    # pending → approved → in_transit → received → rejected

    created_by = db.Column(db.Integer)
    approved_by = db.Column(db.Integer)

    created_at = db.Column(db.DateTime)
class TransferItem(db.Model):
    __tablename__ = "transfer_items"

    id = db.Column(db.Integer, primary_key=True)

    transfer_id = db.Column(db.Integer, db.ForeignKey("transfers.id"))
    product_id = db.Column(db.Integer)

    quantity_requested = db.Column(db.Integer)
    quantity_sent = db.Column(db.Integer)
    quantity_received = db.Column(db.Integer)
class TransitInventory(db.Model):
    __tablename__ = "transit_inventory"

    id = db.Column(db.Integer, primary_key=True)

    transfer_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    quantity = db.Column(db.Integer)