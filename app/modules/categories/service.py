from app.extensions import db
from app.modules.categories.models import Category


class CategoryService:

    @staticmethod
    def create_category(
        tenant_id,
        name,
        parent_id=None
    ):

        category = Category(
            tenant_id=tenant_id,
            name=name,
            parent_id=parent_id
        )

        db.session.add(category)
        db.session.commit()

        return category

    @staticmethod
    def get_categories_by_tenant(tenant_id):

        return Category.query.filter_by(
            tenant_id=tenant_id,
            is_active=True
        ).order_by(Category.name).all()

    @staticmethod
    def get_category(category_id):

        return Category.query.get(category_id)