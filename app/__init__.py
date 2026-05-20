from datetime import timedelta

from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_migrate import Migrate

from app.config import Config
from app.extensions import db, login_manager

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=3)

    # -----------------------
    # INIT EXTENSIONS
    # -----------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 🔥 IMPORTANT (fix login loop issues)
    login_manager.login_view = "auth.login"

    # -----------------------
    # IMPORT MODELS (REQUIRED)
    # -----------------------
    from app.modules.users.models import User
    from app.modules.tenants.models import Tenant
    from app.modules.brands.models import Brand
    from app.modules.branches.models import Branch
    from app.modules.products.models import Product
    from app.modules.warehouses.models import Warehouse
    from app.modules.inventory.models import Inventory
    from app.modules.orders.models import Order
    from app.modules.transfers.models import (
        Transfer,
        TransferItem,
        TransitInventory
    )

    # ✅ IMPORT NOTIFICATION MODEL
    from app.modules.notifications.models import Notification
    from app.modules.product_variants.models import ProductVariant
    from app.modules.stock_reservations.models import StockReservation
    from app.modules.cart.models import Cart, CartItem

    # -----------------------
    # LOGIN MANAGER
    # -----------------------
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # -----------------------
    # 🔔 GLOBAL NOTIFICATIONS
    # -----------------------
    @app.context_processor
    def inject_notifications():

      if not current_user.is_authenticated:
        return dict(notifications=[])

      notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
      ).order_by(
        Notification.created_at.desc()
      ).limit(10).all()

      return dict(notifications=notifications)

    # -----------------------
    # BLUEPRINTS
    # -----------------------
    from app.auth.routes import auth_bp
    from app.modules.products.routes import products_bp
    from app.modules.inventory.routes import inventory_bp
    from app.modules.stock_movements.routes import movements_bp
    from app.modules.orders.routes import orders_bp
    from app.modules.payments.routes import payments_bp
    from app.modules.transfers.routes import transfers_bp
    from app.admin.routes import admin_bp
    from app.tenant.routes import tenant_bp
    from app.modules.branches.routes import branch_bp
    from app.modules.notifications.routes import notifications_bp
    from app.modules.categories.routes import categories_bp
    from app.modules.size_scales.routes import size_scales_bp
    from app.modules.product_variants.routes import variants_bp
    from app.modules.colors.routes  import colors_bp
    from app.modules.pricing.routes import pricing_bp
    from app.modules.segment.routes import segments_bp
    from app.modules.line.routes import lines_bp
    from app.modules.style.routes import styles_bp

    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(movements_bp, url_prefix="/movements")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(transfers_bp, url_prefix="/transfers")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(tenant_bp, url_prefix="/tenant")
    app.register_blueprint(branch_bp, url_prefix="/branch")
    app.register_blueprint(categories_bp)
    app.register_blueprint(size_scales_bp)
    app.register_blueprint(variants_bp)
    app.register_blueprint(colors_bp)
    app.register_blueprint(pricing_bp)
    app.register_blueprint(segments_bp)
    app.register_blueprint(lines_bp)
    app.register_blueprint(styles_bp)
    # -----------------------
    # ROOT ROUTE
    # -----------------------
    @app.route("/")
    def home():

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        role = (
            getattr(current_user, "role", "") or ""
        ).strip().lower()

        if role == "admin":
            return redirect(url_for("admin.dashboard"))

        elif role == "tenant":
            return redirect(url_for("tenant.dashboard"))

        elif role in [
            "branch_admin",
            "branch_manager",
            "vendor"
        ]:
            return redirect(url_for("branch.dashboard"))

        return redirect(url_for("auth.login"))

    # -----------------------
    # DEBUG ROUTE
    # -----------------------
    @app.route("/debug-user")
    def debug_user():

        return {
            "authenticated": current_user.is_authenticated,
            "id": getattr(current_user, "id", None),
            "role": getattr(current_user, "role", None),
        }

    return app