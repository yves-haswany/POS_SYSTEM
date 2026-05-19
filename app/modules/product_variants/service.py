from app import db
from app.modules.product_variants.models import ProductVariant
class ProductVariantService:

    @staticmethod
    def create_variant(data):
        variant = ProductVariant(**data)
        db.session.add(variant)
        db.session.commit()
        return variant

    @staticmethod
    def get_by_product(product_id):
        return ProductVariant.query.filter_by(product_id=product_id).all()