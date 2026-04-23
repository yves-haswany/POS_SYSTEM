from app import create_app
from app.modules.orders.models import Order

app = create_app()

def push_order(provider, order_id):
    with app.app_context():
        order = Order.query.get(order_id)
        provider.push_order(order)