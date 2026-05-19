from datetime import datetime, timedelta
from .models import StockReservation
from app.extensions import db


class StockReservationService:

    @staticmethod
    def reserve(cart_id, variant_id, branch_id, qty, ttl_minutes=10):

        reservation = StockReservation(
            cart_id=cart_id,
            product_variant_id=variant_id,
            branch_id=branch_id,
            quantity=qty,
            status="reserved",
            expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes)
        )

        db.session.add(reservation)
        db.session.commit()
        return reservation

    @staticmethod
    def release_expired():
        now = datetime.utcnow()

        StockReservation.query.filter(
            StockReservation.status == "reserved",
            StockReservation.expires_at < now
        ).update({"status": "expired"})

        db.session.commit()