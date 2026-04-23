from flask import Blueprint, request, jsonify
from app.extensions import db
from app.modules.payments.models import Payment

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/", methods=["POST"])
def create_payment():
    data = request.json

    payment = Payment(
        order_id=data["order_id"],
        amount=data["amount"],
        method=data["method"]
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify({"id": payment.id})