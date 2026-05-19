from app.extensions import db
from app.modules.warehouses.models import Warehouse


def create_brand_main_warehouse(brand):
    """
    Create ONE main warehouse per brand
    """

    existing = Warehouse.query.filter_by(
        brand_id=brand.id,
        branch_id=None
    ).first()

    if existing:
        return existing

    warehouse = Warehouse(
        name=f"{brand.name} Main Warehouse",
        tenant_id=brand.tenant_id,
        brand_id=brand.id,
        branch_id=None
    )

    db.session.add(warehouse)
    db.session.flush()

    return warehouse


def create_branch_warehouse(branch):
    from app.modules.warehouses.models import Warehouse

    # 🔥 get main warehouse
    main = Warehouse.query.filter_by(
        brand_id=branch.brand_id,
        branch_id=None
    ).first()

    warehouse = Warehouse(
        name=f"{branch.name} Warehouse",
        tenant_id=branch.tenant_id,
        brand_id=branch.brand_id,
        branch_id=branch.id,
        parent_id=main.id if main else None
    )

    db.session.add(warehouse)
    db.session.flush()

    return warehouse