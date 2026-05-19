from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.modules.transfers.models import (
    Transfer,
    TransferItem,
    TransitInventory
)
from app.modules.warehouses.models import Warehouse
from app.modules.inventory.models import Inventory
from app.modules.products.models import Product
from app.modules.brands.models import Brand
from app.modules.notifications.utils import create_notification

# ✅ NEW
from app.modules.stock_movements.service import StockMovementService

from app.core.constants.roles import (
    ROLE_BRANCH_ADMIN,
    ROLE_BRANCH_MANAGER,
    ROLE_VENDOR
)

transfers_bp = Blueprint(
    "transfers",
    __name__,
    url_prefix="/transfers"
)


# =====================================================
# 🔹 HELPERS
# =====================================================
def tenant_scope_filter(query):
    return query.filter(
        Transfer.tenant_id == current_user.tenant_id
    )


def is_branch_user():
    return current_user.role in [
        ROLE_BRANCH_ADMIN,
        ROLE_BRANCH_MANAGER,
        ROLE_VENDOR
    ]


# =====================================================
# 🔹 LIST TRANSFERS
# =====================================================
@transfers_bp.route("/")
@login_required
def list_transfers():

    transfers = tenant_scope_filter(
        Transfer.query
    ).all()

    incoming_count = Transfer.query.join(
        Warehouse,
        Transfer.destination_warehouse_id == Warehouse.id
    ).filter(
        Warehouse.branch_id == current_user.branch_id,
        Transfer.status == "in_transit"
    ).count()

    return render_template(
        "transfers/list.html",
        transfers=transfers,
        incoming_count=incoming_count
    )


# =====================================================
# 🔹 CREATE TRANSFER
# =====================================================
@transfers_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_transfer():

    warehouses = Warehouse.query.join(Brand).filter(
        Brand.tenant_id == current_user.tenant_id
    ).all()

    inventory = []
    selected_source = None

    # =====================================================
    # LOAD INVENTORY
    # =====================================================
    if request.method == "POST" and request.form.get("load_inventory"):

        selected_source = int(
            request.form.get("source_warehouse_id")
        )

        inventory = Inventory.query.filter_by(
            warehouse_id=selected_source
        ).all()

        return render_template(
            "transfers/create.html",
            warehouses=warehouses,
            inventory=inventory,
            selected_source=selected_source
        )

    # =====================================================
    # CREATE TRANSFER
    # =====================================================
    if request.method == "POST" and request.form.get("create_transfer"):

        source_id = int(
            request.form.get("source_warehouse_id")
        )

        destination_id = int(
            request.form.get("destination_warehouse_id")
        )

        source = Warehouse.query.get_or_404(source_id)
        destination = Warehouse.query.get_or_404(destination_id)

        # 🔒 Tenant security
        if source.brand.tenant_id != current_user.tenant_id:
            abort(403)

        if destination.brand.tenant_id != current_user.tenant_id:
            abort(403)

        # ❌ Same warehouse
        if source_id == destination_id:

            flash(
                "Source and destination cannot be the same",
                "danger"
            )

            return redirect(
                url_for("transfers.create_transfer")
            )

        # =====================================================
        # CREATE TRANSFER
        # =====================================================
        transfer = Transfer(
            tenant_id=current_user.tenant_id,
            source_warehouse_id=source_id,
            destination_warehouse_id=destination_id,
            status="draft",
            created_by=current_user.id,
            created_at=datetime.utcnow()
        )

        db.session.add(transfer)
        db.session.flush()

        created_items = 0

        # =====================================================
        # CREATE ITEMS
        # =====================================================
        for key, value in request.form.items():

            if not key.startswith("qty_"):
                continue

            product_id = int(key.split("_")[1])
            qty = int(value or 0)

            if qty <= 0:
                continue

            inventory_item = Inventory.query.filter_by(
                warehouse_id=source_id,
                product_id=product_id
            ).first()

            if not inventory_item:
                continue

            if inventory_item.quantity < qty:

                flash(
                    f"Not enough stock for "
                    f"{inventory_item.product.name}",
                    "danger"
                )

                db.session.rollback()

                return redirect(
                    url_for("transfers.create_transfer")
                )

            item = TransferItem(
                transfer_id=transfer.id,
                product_id=product_id,
                quantity_requested=qty,
                quantity_sent=0,
                quantity_received=0
            )

            db.session.add(item)

            created_items += 1

        if created_items == 0:

            db.session.rollback()

            flash(
                "Add at least one product",
                "danger"
            )

            return redirect(
                url_for("transfers.create_transfer")
            )

        db.session.commit()

        flash(
            "Transfer draft created successfully",
            "success"
        )

        return redirect(
            url_for("transfers.list_transfers")
        )

    return render_template(
        "transfers/create.html",
        warehouses=warehouses,
        inventory=inventory,
        selected_source=selected_source
    )

# =====================================================
# 🔹 VIEW TRANSIT
# =====================================================
@transfers_bp.route("/transit")
@login_required
def view_transit():

    transfers = Transfer.query.join(
        Warehouse,
        Transfer.destination_warehouse_id == Warehouse.id
    ).filter(
        Warehouse.branch_id == current_user.branch_id,
        Transfer.status == "in_transit"
    ).all()

    return render_template(
        "transfers/transit.html",
        transfers=transfers
    )

# =====================================================
# 🔹 ADD ITEMS
# =====================================================
@transfers_bp.route("/<int:transfer_id>/items", methods=["GET", "POST"])
@login_required
def add_items(transfer_id):

    transfer = Transfer.query.get_or_404(
        transfer_id
    )

    if transfer.tenant_id != current_user.tenant_id:
        abort(403)

    if request.method == "GET":

        inventory = Inventory.query.filter_by(
            warehouse_id=transfer.source_warehouse_id
        ).all()

        return render_template(
            "transfers/items.html",
            transfer=transfer,
            inventory=inventory
        )

    # =====================================================
    # POST
    # =====================================================
    product_id = int(request.form.get("product_id"))
    quantity = int(request.form.get("quantity"))

    item = TransferItem(
        transfer_id=transfer.id,
        product_id=product_id,
        quantity_requested=quantity,
        quantity_sent=0,
        quantity_received=0
    )

    db.session.add(item)
    db.session.commit()

    return redirect(
        url_for(
            "transfers.add_items",
            transfer_id=transfer.id
        )
    )
@transfers_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_transfer(id):

    transfer = Transfer.query.get_or_404(id)

    if transfer.tenant_id != current_user.tenant_id:
        abort(403)

    if transfer.status != "draft":
        flash("Only draft transfers can be edited", "warning")
        return redirect(url_for("transfers.list_transfers"))

    if request.method == "POST":

        transfer.notes = request.form.get("notes")

        db.session.commit()

        flash("Transfer updated", "success")

        return redirect(url_for("transfers.list_transfers"))

    return render_template(
        "transfers/edit.html",
        transfer=transfer
    )
# =====================================================
# 🔹 SEND TRANSFER
# =====================================================
@transfers_bp.route("/<int:id>/send")
@login_required
def send_transfer(id):

    transfer = Transfer.query.get_or_404(id)

    if transfer.status != "draft":
        abort(400, "Only draft transfers can be sent")

    items = TransferItem.query.filter_by(
        transfer_id=id
    ).all()

    if not items:
        abort(400, "Transfer has no items")

    # =====================================================
    # VALIDATE STOCK FIRST
    # =====================================================
    for item in items:

        inventory = Inventory.query.filter_by(
            warehouse_id=transfer.source_warehouse_id,
            product_id=item.product_id
        ).first()

        if not inventory or inventory.quantity < item.quantity_requested:
            abort(400, f"Not enough stock for product {item.product_id}")

    # =====================================================
    # APPLY MOVEMENT (SAFE SINGLE PASS)
    # =====================================================
    for item in items:

        inventory = Inventory.query.filter_by(
            warehouse_id=transfer.source_warehouse_id,
            product_id=item.product_id
        ).first()

        inventory.quantity -= item.quantity_requested

        StockMovementService.create_stock_movement(
            tenant_id=current_user.tenant_id,
            product_id=item.product_id,
            warehouse_id=transfer.source_warehouse_id,
            from_warehouse_id=transfer.source_warehouse_id,
            to_warehouse_id=transfer.destination_warehouse_id,
            quantity=-item.quantity_requested,
            movement_type="transfer_out",
            reference=f"Transfer #{transfer.id}",
            created_by=current_user.id
        )

        db.session.add(
            TransitInventory(
                transfer_id=transfer.id,
                product_id=item.product_id,
                quantity=item.quantity_requested
            )
        )

        item.quantity_sent = item.quantity_requested

    transfer.status = "in_transit"

    # =====================================================
    # NOTIFICATIONS
    # =====================================================
    destination = Warehouse.query.get(transfer.destination_warehouse_id)

    if destination:

        from app.modules.users.models import User

        users = User.query.filter_by(
            branch_id=destination.branch_id
        ).all()

        for user in users:
            create_notification(
                user_id=user.id,
                message=f"📦 Transfer #{transfer.id} is awaiting approval",
                type="transfer"
            )

    db.session.commit()

    flash(f"Transfer #{transfer.id} sent successfully", "success")

    return redirect(url_for("transfers.list_transfers"))


# =====================================================
# REJECT TRANSFER (FIXED)
# =====================================================
@transfers_bp.route("/<int:id>/reject", methods=["POST"])
@login_required
def reject_transfer(id):

    transfer = Transfer.query.get_or_404(id)

    if transfer.status != "in_transit":
        abort(400)

    items = TransferItem.query.filter_by(
        transfer_id=id
    ).all()

    for item in items:

        TransitInventory.query.filter_by(
            transfer_id=id,
            product_id=item.product_id
        ).delete()

        StockMovementService.create_stock_movement(
            tenant_id=current_user.tenant_id,
            product_id=item.product_id,
            warehouse_id=transfer.source_warehouse_id,
            from_warehouse_id=transfer.destination_warehouse_id,
            to_warehouse_id=transfer.source_warehouse_id,
            quantity=item.quantity_sent,
            movement_type="transfer_revert",
            reference=f"Transfer #{transfer.id} (rejected)",
            created_by=current_user.id
        )

        item.quantity_received = 0

    transfer.status = "rejected"

    from app.modules.notifications.models import Notification

    Notification.query.filter(
        Notification.type == "transfer",
        Notification.message.contains(f"Transfer #{transfer.id}")
    ).delete(synchronize_session=False)

    source = Warehouse.query.get(transfer.source_warehouse_id)

    if source:

        from app.modules.users.models import User

        users = User.query.filter_by(
            branch_id=source.branch_id
        ).all()

        for user in users:
            create_notification(
                user_id=user.id,
                message=f"❌ Transfer #{transfer.id} was rejected",
                type="transfer"
            )

    db.session.commit()

    flash("Transfer rejected", "warning")

    return redirect(url_for("transfers.view_transit"))


# =====================================================
# ACCEPT TRANSFER (FIXED)
# =====================================================
@transfers_bp.route("/<int:id>/accept", methods=["POST"])
@login_required
def accept_transfer(id):

    transfer = Transfer.query.get_or_404(id)

    if transfer.status != "in_transit":
        abort(400)

    items = TransferItem.query.filter_by(
        transfer_id=id
    ).all()

    for item in items:

        inventory = Inventory.query.filter_by(
            warehouse_id=transfer.destination_warehouse_id,
            product_id=item.product_id
        ).first()

        if not inventory:
            inventory = Inventory(
                warehouse_id=transfer.destination_warehouse_id,
                product_id=item.product_id,
                quantity=0
            )
            db.session.add(inventory)

        inventory.quantity += item.quantity_sent

        StockMovementService.create_stock_movement(
            tenant_id=current_user.tenant_id,
            product_id=item.product_id,
            warehouse_id=transfer.destination_warehouse_id,
            from_warehouse_id=transfer.source_warehouse_id,
            to_warehouse_id=transfer.destination_warehouse_id,
            quantity=item.quantity_sent,
            movement_type="transfer_in",
            reference=f"Transfer #{transfer.id}",
            created_by=current_user.id
        )

        TransitInventory.query.filter_by(
            transfer_id=id,
            product_id=item.product_id
        ).delete()

        item.quantity_received = item.quantity_sent

    transfer.status = "received"

    from app.modules.notifications.models import Notification

    Notification.query.filter(
        Notification.type == "transfer",
        Notification.message.contains(f"Transfer #{transfer.id}")
    ).delete(synchronize_session=False)

    source = Warehouse.query.get(transfer.source_warehouse_id)

    if source:

        from app.modules.users.models import User

        users = User.query.filter_by(
            branch_id=source.branch_id
        ).all()

        for user in users:
            create_notification(
                user_id=user.id,
                message=f"✅ Transfer #{transfer.id} was accepted",
                type="transfer"
            )

    db.session.commit()

    flash("Transfer accepted", "success")

    return redirect(url_for("transfers.view_transit"))

# =====================================================
# 🔹 DELETE TRANSFER
# =====================================================
@transfers_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete_transfer(id):

    transfer = Transfer.query.get_or_404(id)

    if transfer.tenant_id != current_user.tenant_id:
        abort(403)

    # ✅ FIXED
    if transfer.status != "draft":

        flash(
            "Only draft transfers can be deleted",
            "error"
        )

        return redirect(
            url_for("transfers.list_transfers")
        )

    TransferItem.query.filter_by(
        transfer_id=id
    ).delete()

    TransitInventory.query.filter_by(
        transfer_id=id
    ).delete()

    db.session.delete(transfer)
    db.session.commit()

    flash(
        "Transfer deleted successfully",
        "success"
    )

    return redirect(
        url_for("transfers.list_transfers")
    )
