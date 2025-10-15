# first_app/services/product_services.py
from first_app.models import Categories, CategoriesProduct, ProductMaster

class ProductServices:
    @staticmethod
    def get_all_with_products():
        categories_data = []
        categories = Categories.objects.all()
        for category in categories:
            products = (
                CategoriesProduct.objects
                .filter(categories=category)
                .select_related('product')
            )

            product_list = [
                {
                    "product_name": p.product.product_name,
                    "image": p.product.image,
                    "base_price": p.product.base_price,
                }
                for p in products
            ]

            categories_data.append({
                "category_name": category.categories_name,
                "products": product_list
            })

        return categories_data
