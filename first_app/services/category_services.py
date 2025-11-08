
# first_app/services/product_services.py
from django.shortcuts import get_object_or_404
from first_app.models import ProductMaster
from first_app.models import Categories
class CategoriesService:
    @staticmethod
    def get_product_detail(product_code):
        product = get_object_or_404(ProductMaster, product_code=product_code)
        return product

    @staticmethod
    def get_suggested_products(product):# sản phẩm gợi ý
        if not product.category:
            return ProductMaster.objects.none()
        return ProductMaster.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(product_code=product.product_code)[:4]

    @staticmethod
    def get_products_by_category(category_id): # lấy sản tất cả sản phẩm theo danh mục
        category = get_object_or_404(Categories, categories_id=category_id)
        products = ProductMaster.objects.filter(category=category, is_active=True)
        return category, products
    @staticmethod
    def get_all_categories(limit=None):#lấy danh mục sản phẩm có thể chỉnh sửa số lượng hiện thay none=
        qs = Categories.objects.all()
        if limit is not None:
            qs = qs[:limit]
        return qs

