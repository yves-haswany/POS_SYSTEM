from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    # Optional direct user target
    user_id = db.Column(db.Integer, nullable=True)

    # NEW: branch-wide target
    branch_id = db.Column(db.Integer, nullable=True)

    message = db.Column(db.String, nullable=False)

    type = db.Column(db.String, default="info")  # transfer, alert, etc.

    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)