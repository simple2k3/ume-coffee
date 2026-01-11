from functools import wraps
from django.shortcuts import get_object_or_404
from first_app.models import Categories, ProductMaster
def register_breadcrumb(title=None): #đây là link di chuyển dữ các trang trangchu/category...
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            # Luôn có Trang chủ
            breadcrumbs = [{'text': 'Trang chủ', 'url': '/'}]
            # Nếu đang xem danh mục sản phẩm
            if 'category_id' in kwargs:
                category = get_object_or_404(Categories, categories_id=kwargs['category_id'])
                breadcrumbs.append({'text': 'Danh Mục', 'url': '/portfolio/'})
                breadcrumbs.append({
                    'text': category.categories_name,
                    'url': f'/category/{category.categories_id}/'
                })
            # Nếu đang xem chi tiết sản phẩm
            elif 'product_code' in kwargs:
                product = get_object_or_404(ProductMaster, product_code=kwargs['product_code'])
                breadcrumbs.append({'text': 'Danh Mục', 'url': '/portfolio/'})
                breadcrumbs.append({
                    'text': product.category.categories_name,
                    'url': f'/category/{product.category.categories_id}/'
                })
                breadcrumbs.append({'text': product.product_name, 'url': None})
            else:
                breadcrumbs.append({'text': 'Danh Mục', 'url': None})

            request.breadcrumbs = breadcrumbs
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
