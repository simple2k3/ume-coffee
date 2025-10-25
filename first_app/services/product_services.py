from first_app.models import Categories, ProductMaster

class ProductsServices:
    @staticmethod
    def getlistproduct():
        categories = Categories.objects.prefetch_related('products').all()
        result = []
        for category in categories:
            result.append({
                'category_id': category.categories_id,
                'category_name': category.categories_name,
                'products': [
                    {
                        'product_code': product.product_code,
                        'product_name': product.product_name,
                        'image': product.image,
                        'base_price': product.base_price,
                        'description': product.description
                    }
                    for product in category.products.filter(is_active=True)
                ]
            })
        return result


