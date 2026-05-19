from flask import Blueprint, request, jsonify
from app.tenants.middleware import get_current_tenant_id
from app.modules.tenants.models import Tenant
from app.modules.orders.service import create_order

api_bp = Blueprint("api", __name__)

@api_bp.route("/orders", methods=["POST"])
def create_order_route():
    tenant_id = get_current_tenant_id()
    tenant = Tenant.query.get(tenant_id)

    data = request.json
    order = create_order(tenant, data["total"])

    return jsonify({"id": order.id})