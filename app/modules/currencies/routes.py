
from flask import Blueprint

from flask import request, jsonify
from app.modules.currencies.service import CurrencyService
currency_bp = Blueprint("currencies", __name__, url_prefix="/currencies")


@currency_bp.route("/convert")
def convert():
    amount = float(request.args.get("amount"))
    from_cur = request.args.get("from")
    to_cur = request.args.get("to")

    rate = CurrencyService.get_latest_rate(from_cur, to_cur)

    return jsonify({
        "converted": amount * rate.rate if rate else None
    })