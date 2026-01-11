
# first_app/services/product_services.py
from django.shortcuts import get_object_or_404
from first_app.models import ProductMaster
from first_app.models import Categories
class CategoriesService:
    @staticmethod
    def get_product_detail(product_code):
        product = get_object_or_404(ProductMaster, product_code=product_code)#lấy sản phẩm trong productmaster nếu không có sản phẩm trả về 404
        return product
    @staticmethod
    def get_suggested_products(product):# sản phẩm gợi ý
        if not product.category:# kiểm tra xem sp hiện tại có thuộc danh mục nào k
            return ProductMaster.objects.none() #trả về danh sách rỗng
        return ProductMaster.objects.filter(
            category=product.category,#tìm sản các sản phẩm có chung danh muchj
            is_active=True#lấy các sản phẩm được bật
        ).exclude(product_code=product.product_code)[:4]#lấy sản phẩm trừ cái đang xem hiện lên 4

    @staticmethod
    def get_products_by_category(category_id): # lấy sản tất cả sản phẩm theo danh mục
        category = get_object_or_404(Categories, categories_id=category_id)
        products = ProductMaster.objects.filter(category=category, is_active=True)#chỉ lấy những sản phẩm nào có trường category khớp với danh mục
        return category, products
    @staticmethod
    def get_all_categories(limit=None):#lấy danh mục sản phẩm có thể chỉnh sửa số lượng hiện thay limit=
        qs = Categories.objects.all()
        if limit is not None:
            qs = qs[:limit]#
        return qs

