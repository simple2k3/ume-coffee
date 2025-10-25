# first_app/utils/breadcrumbs.py
from functools import wraps
from first_app.models import Categories
from first_app.models import ProductMaster
def register_breadcrumb(title=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            breadcrumbs = [{'text': 'Trang chủ', 'url': '/'}]
            # Trang danh mục
            if 'category_id' in kwargs:
                category = Categories.objects.get(categories_id=kwargs['category_id'])
                breadcrumbs.append({'text': 'Sản phẩm', 'url': '/portfolio/'})
                breadcrumbs.append({'text': category.categories_name, 'url': f'/category/{category.categories_id}/'})

            # Trang chi tiết sản phẩm
            elif 'product_code' in kwargs:
                product = ProductMaster.objects.get(product_code=kwargs['product_code'])
                breadcrumbs.append({'text': 'Sản phẩm', 'url': '/portfolio/'})
                breadcrumbs.append({'text': product.category.categories_name,
                                    'url': f'/category/{product.category.categories_id}/'})
                breadcrumbs.append({'text': product.product_name, 'url': None})
            else:
                breadcrumbs.append({'text': 'Sản phẩm', 'url': None})

            request.breadcrumbs = breadcrumbs
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
