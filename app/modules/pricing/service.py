from app.modules.pricing.models import PriceListItem, PriceList
from app.modules.product_variants.models import ProductVariant

class PricingService:

    @staticmethod
    def get_price(variant_id, price_list_id):

        # 1. Validate price list exists
        price_list = PriceList.query.filter_by(
            id=price_list_id
        ).first()

        if not price_list:
            return None

        # 2. Get price item
        item = PriceListItem.query.filter_by(
            product_variant_id=variant_id,
            price_list_id=price_list_id
        ).first()

        if item:
            return item.price

        # 3. FALLBACK: variant base price (VERY IMPORTANT)
        variant = ProductVariant.query.get(variant_id)

        if variant:
            return variant.price  # assuming you have it

        return None