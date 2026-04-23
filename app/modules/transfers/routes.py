from flask import Blueprint, request, jsonify
from app.extensions import db
from app.modules.transfers.models import Transfer
from app.modules.transfers.service import execute_transfer

transfers_bp = Blueprint("transfers", __name__)

@transfers_bp.route("/", methods=["POST"])
def create_transfer():
    data = request.json

    transfer = Transfer(
        from_location_id=data["from_location_id"],
        to_location_id=data["to_location_id"]
    )

    db.session.add(transfer)
    db.session.commit()

    return jsonify({"id": transfer.id})


@transfers_bp.route("/<int:transfer_id>/execute", methods=["POST"])
def run_transfer(transfer_id):
    data = request.json

    transfer = Transfer.query.get_or_404(transfer_id)

    execute_transfer(transfer, data["items"])

    return jsonify({"status": "completed"})