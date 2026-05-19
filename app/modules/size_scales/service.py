from app.extensions import db

from app.modules.size_scales.models import (
    SizeScale,
    SizeScaleItem
)


class SizeScaleService:

    @staticmethod
    def create_scale(
        tenant_id,
        name
    ):

        scale = SizeScale(
            tenant_id=tenant_id,
            name=name
        )

        db.session.add(scale)
        db.session.commit()

        return scale

    @staticmethod
    def add_size(
        size_scale_id,
        value,
        sort_order=0
    ):

        item = SizeScaleItem(
            size_scale_id=size_scale_id,
            value=value,
            sort_order=sort_order
        )

        db.session.add(item)
        db.session.commit()

        return item