from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    session
)

from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.extensions import db

from app.modules.products.models import Product
from app.modules.orders.models import Order, OrderItem
from app.modules.users.models import User
from app.modules.inventory.models import Inventory
from app.modules.transfers.models import Transfer, TransferItem
from app.modules.warehouses.models import Warehouse

from app.core.constants.roles import (
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)

# =====================================================
# BLUEPRINT
# =====================================================
branch_bp = Blueprint("branch", __name__, url_prefix="/branch")


# =====================================================
# 🔐 ROLE DECORATOR
# =====================================================
def require_roles(*roles):

    def wrapper(fn):

        from functools import wraps

        @wraps(fn)
        def decorated(*args, **kwargs):

            if current_user.role not in roles:
                abort(403)

            return fn(*args, **kwargs)

        return decorated

    return wrapper


# =====================================================
# 🔐 BRANCH SCOPE
# =====================================================
def require_branch_scope(obj):

    if obj.branch_id != current_user.branch_id:
        abort(403)


# =====================================================
# 🔹 GET BRANCH INVENTORY ITEM
# =====================================================
def get_branch_inventory(product_id):

    return Inventory.query.join(
        Warehouse,
        Inventory.warehouse_id == Warehouse.id
    ).filter(
        Warehouse.branch_id == current_user.branch_id,
        Inventory.product_id == product_id
    ).first()


# =====================================================
# 🔹 POS DASHBOARD
# =====================================================
@branch_bp.route("/dashboard")
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def dashboard():

    from app.modules.branches.models import Branch

    inventory_items = Inventory.query.join(
        Warehouse,
        Inventory.warehouse_id == Warehouse.id
    ).filter(
        Warehouse.branch_id == current_user.branch_id
    ).all()

    invoice_cart = session.get("invoice_cart", [])

    incoming_transfers = Transfer.query.join(
        Warehouse,
        Transfer.destination_warehouse_id == Warehouse.id
    ).filter(
        Warehouse.branch_id == current_user.branch_id,
        Transfer.status == "in_transit"
    ).all()

    branches = Branch.query.filter(
        Branch.tenant_id == current_user.tenant_id,
        Branch.id != current_user.branch_id
    ).all()

    warehouses = Warehouse.query.filter(
        Warehouse.tenant_id == current_user.tenant_id,
        Warehouse.branch_id.is_(None)
    ).all()

    return render_template(
        "branch/pos.html",
        inventory_items=inventory_items,
        invoice_cart=invoice_cart,
        incoming_transfers=incoming_transfers,
        branches=branches,
        warehouses=warehouses
    )


@branch_bp.route("/transfers/create", methods=["POST"])
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def create_transfer():

    destination_type = request.form.get("destination_type")
    destination_id = int(request.form.get("destination_id"))

    transfer = Transfer(
        tenant_id=current_user.tenant_id,
        source_branch_id=current_user.branch_id,
        created_by=current_user.id,
        status="draft"
    )

    if destination_type == "branch":

        transfer.destination_branch_id = destination_id
        transfer.destination_warehouse_id = None

    elif destination_type == "warehouse":

        transfer.destination_warehouse_id = destination_id
        transfer.destination_branch_id = None

    else:

        flash("Invalid destination type", "danger")

        return redirect(
            url_for("branch.dashboard")
        )

    db.session.add(transfer)
    db.session.commit()

    flash(
        "Transfer created",
        "success"
    )

    return redirect(
        url_for(
            "branch.edit_transfer",
            id=transfer.id
        )
    )

# =====================================================
# 🔹 ORDERS LIST
# =====================================================
@branch_bp.route("/orders")
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def list_orders():

    query = Order.query.filter_by(
        branch_id=current_user.branch_id
    )

    if current_user.role == ROLE_VENDOR:

        query = query.filter_by(
            created_by=current_user.id
        )

    orders = query.order_by(Order.id.desc()).all()

    return render_template(
        "branch/orders/list.html",
        orders=orders
    )


# =====================================================
# 🔹 VIEW INVOICE
# =====================================================
@branch_bp.route("/orders/<int:id>/invoice")
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def order_invoice(id):

    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).get_or_404(id)

    if order.tenant_id != current_user.tenant_id:
        abort(403)

    if order.branch_id != current_user.branch_id:
        abort(403)

    subtotal = sum(
        item.quantity * item.price
        for item in order.items
    )

    discount = getattr(order, "discount", 0) or 0

    return render_template(
        "branch/orders/invoice.html",
        order=order,
        subtotal=subtotal,
        discount=discount
    )


# =====================================================
# 🔹 SCAN BARCODE
# =====================================================
@branch_bp.route("/pos/scan", methods=["POST"])
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def scan_barcode():

    barcode = request.form.get("barcode", "").strip()

    quantity = int(
        request.form.get("quantity", 1)
    )

    if not barcode:

        flash("Barcode is required", "danger")

        return redirect(
            url_for("branch.dashboard")
        )

    product = Product.query.filter_by(
        barcode=barcode
    ).first()

    if not product:

        flash("Product not found", "danger")

        return redirect(
            url_for("branch.dashboard")
        )

    inventory = get_branch_inventory(product.id)

    if not inventory:

        flash("Product not available in branch", "danger")

        return redirect(
            url_for("branch.dashboard")
        )

    invoice_cart = session.get("invoice_cart", [])

    found = False

    for item in invoice_cart:

        if item["product_id"] == product.id:

            new_quantity = item["quantity"] + quantity

            if new_quantity > inventory.quantity:

                flash(
                    f"Only {inventory.quantity} available",
                    "danger"
                )

                return redirect(
                    url_for("branch.dashboard")
                )

            item["quantity"] = new_quantity

            found = True
            break

    if not found:

        if quantity > inventory.quantity:

            flash(
                f"Only {inventory.quantity} available",
                "danger"
            )

            return redirect(
                url_for("branch.dashboard")
            )

        invoice_cart.append({
            "product_id": product.id,
            "barcode": product.barcode,
            "name": product.name,
            "price": float(product.price),
            "quantity": quantity
        })

    session["invoice_cart"] = invoice_cart

    flash(
        f"{product.name} added",
        "success"
    )

    return redirect(
        url_for("branch.dashboard")
    )


# =====================================================
# 🔹 UPDATE ITEM QUANTITY
# =====================================================
@branch_bp.route(
    "/pos/item/<int:product_id>/quantity",
    methods=["POST"]
)
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def update_invoice_quantity(product_id):

    quantity = int(
        request.form.get("quantity", 1)
    )

    if quantity <= 0:
        quantity = 1

    inventory = get_branch_inventory(product_id)

    if not inventory:

        flash("Inventory missing", "danger")

        return redirect(
            url_for("branch.dashboard")
        )

    if quantity > inventory.quantity:

        flash(
            f"Only {inventory.quantity} available",
            "danger"
        )

        return redirect(
            url_for("branch.dashboard")
        )

    invoice_cart = session.get("invoice_cart", [])

    for item in invoice_cart:

        if item["product_id"] == product_id:

            item["quantity"] = quantity
            break

    session["invoice_cart"] = invoice_cart

    flash(
        "Quantity updated",
        "success"
    )

    return redirect(
        url_for("branch.dashboard")
    )


# =====================================================
# 🔹 REMOVE ITEM
# =====================================================
@branch_bp.route(
    "/pos/item/<int:product_id>/remove",
    methods=["POST"]
)
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def remove_invoice_item(product_id):

    invoice_cart = session.get("invoice_cart", [])

    invoice_cart = [
        item for item in invoice_cart
        if item["product_id"] != product_id
    ]

    session["invoice_cart"] = invoice_cart

    flash(
        "Item removed",
        "success"
    )

    return redirect(
        url_for("branch.dashboard")
    )


# =====================================================
# 🔹 CLEAR INVOICE
# =====================================================
@branch_bp.route("/pos/clear", methods=["POST"])
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def clear_invoice():

    session["invoice_cart"] = []

    flash(
        "Invoice cleared",
        "success"
    )

    return redirect(
        url_for("branch.dashboard")
    )


# =====================================================
# 🔹 CREATE INVOICE / CHECKOUT
# =====================================================
@branch_bp.route("/pos/checkout", methods=["POST"])
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def checkout():

    invoice_cart = session.get("invoice_cart", [])

    if not invoice_cart:

        flash(
            "Invoice is empty",
            "danger"
        )

        return redirect(
            url_for("branch.dashboard")
        )

    subtotal = 0

    order = Order(
        tenant_id=current_user.tenant_id,
        branch_id=current_user.branch_id,
        created_by=current_user.id,
        total=0,
        created_at=datetime.utcnow()
    )

    db.session.add(order)
    db.session.flush()

    for cart_item in invoice_cart:

        inventory = get_branch_inventory(
            cart_item["product_id"]
        )

        if not inventory:

            db.session.rollback()

            flash(
                f"{cart_item['name']} inventory missing",
                "danger"
            )

            return redirect(
                url_for("branch.dashboard")
            )

        if inventory.quantity < cart_item["quantity"]:

            db.session.rollback()

            flash(
                f"Not enough stock for {cart_item['name']}",
                "danger"
            )

            return redirect(
                url_for("branch.dashboard")
            )

        inventory.quantity -= cart_item["quantity"]

        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item["product_id"],
            quantity=cart_item["quantity"],
            price=cart_item["price"]
        )

        db.session.add(order_item)

        subtotal += (
            cart_item["quantity"] *
            cart_item["price"]
        )

    discount = float(
        request.form.get("discount", 0)
    )

    final_total = max(
        subtotal - discount,
        0
    )

    order.total = final_total

    if hasattr(order, "discount"):
        order.discount = discount

    db.session.commit()

    session["invoice_cart"] = []

    flash(
        f"Invoice #{order.id} created successfully",
        "success"
    )

    return redirect(
        url_for(
            "branch.order_invoice",
            id=order.id
        )
    )


# =====================================================
# 🔹 USERS LIST
# =====================================================
@branch_bp.route("/users")
@login_required
@require_roles(ROLE_BRANCH_ADMIN)
def list_users():

    users = User.query.filter_by(
        branch_id=current_user.branch_id
    ).all()

    return render_template(
        "branch/users/list.html",
        users=users
    )


# =====================================================
# 🔹 CREATE USER
# =====================================================
@branch_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@require_roles(ROLE_BRANCH_ADMIN)
def create_user():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if role not in [
            ROLE_BRANCH_MANAGER,
            ROLE_VENDOR
        ]:
            abort(403)

        existing = User.query.filter_by(
            username=username
        ).first()

        if existing:

            flash(
                "Username already exists",
                "danger"
            )

            return redirect(
                url_for("branch.create_user")
            )

        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "User created",
            "success"
        )

        return redirect(
            url_for("branch.list_users")
        )

    return render_template(
        "branch/users/create.html"
    )


# =====================================================
# 🔹 EDIT USER
# =====================================================
@branch_bp.route("/users/<int:id>/edit", methods=["GET", "POST"])
@login_required
@require_roles(ROLE_BRANCH_ADMIN)
def edit_user(id):

    user = User.query.get_or_404(id)

    require_branch_scope(user)

    if request.method == "POST":

        user.username = request.form.get("username")

        role = request.form.get("role")

        if role not in [
            ROLE_BRANCH_MANAGER,
            ROLE_VENDOR
        ]:
            abort(403)

        user.role = role

        password = request.form.get("password")

        if password:
            user.password = generate_password_hash(password)

        db.session.commit()

        flash(
            "User updated",
            "success"
        )

        return redirect(
            url_for("branch.list_users")
        )

    return render_template(
        "branch/users/edit.html",
        user=user
    )


# =====================================================
# 🔹 DELETE USER
# =====================================================
@branch_bp.route("/users/<int:id>/delete", methods=["POST"])
@login_required
@require_roles(ROLE_BRANCH_ADMIN)
def delete_user(id):

    user = User.query.get_or_404(id)

    require_branch_scope(user)

    if user.id == current_user.id:

        flash(
            "You cannot delete yourself",
            "danger"
        )

        return redirect(
            url_for("branch.list_users")
        )

    db.session.delete(user)
    db.session.commit()

    flash(
        "User deleted",
        "success"
    )

    return redirect(
        url_for("branch.list_users")
    )
@branch_bp.route("/discounts", methods=["GET", "POST"])
@login_required
@require_roles(ROLE_BRANCH_ADMIN, ROLE_BRANCH_MANAGER)
def manage_discounts():

    return render_template("branch/manage_discounts.html")
@branch_bp.route("/inventory")
@login_required
@require_roles(
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)
def inventory():

    inventory_items = Inventory.query.join(
        Warehouse,
        Inventory.warehouse_id == Warehouse.id
    ).filter(
        Warehouse.branch_id == current_user.branch_id
    ).all()

    return render_template(
        "branch/inventory.html",
        inventory_items=inventory_items
    )