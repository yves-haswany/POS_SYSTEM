from datetime import timedelta

from flask import Flask, redirect, url_for
from flask_login import current_user

from app.config import Config
from app.extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=3)


    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import models (IMPORTANT)
    from app.core.models.user import User
    from app.core.models.tenant import Tenant

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -----------------------
    # BLUEPRINTS (IMPORT ONCE)
    # -----------------------

    from app.auth.routes import auth_bp
    from app.modules.products.routes import products_bp
    from app.modules.locations.routes import locations_bp
    from app.modules.inventory.routes import inventory_bp
    from app.modules.stock_movements.routes import movements_bp
    from app.modules.orders.routes import orders_bp
    from app.modules.payments.routes import payments_bp
    from app.modules.transfers.routes import transfers_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(locations_bp, url_prefix="/locations")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(movements_bp, url_prefix="/movements")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    from app.auth.routes import auth_bp
    app.register_blueprint(transfers_bp, url_prefix="/transfers")
    from app.admin.routes import admin_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.tenant.routes import tenant_bp

    app.register_blueprint(tenant_bp, url_prefix="/tenant")
    # -----------------------
    # ROOT ROUTE
    # -----------------------
    @app.route("/")
    def home():
     if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

     role = (getattr(current_user, "role", "") or "").strip().lower()

     if role == "admin":
        return redirect("/admin/dashboard")
     elif role == "tenant":
        return redirect("/tenant/dashboard")
     elif role == "branch":
        return redirect("/branch/pos")

     return redirect(url_for("auth.login"))
    @app.route("/debug-user")
    def debug_user():
        return {
            "authenticated": current_user.is_authenticated,
            "id": getattr(current_user, "id", None),
            "role": getattr(current_user, "role", None),
        }
    return app