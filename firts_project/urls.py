
from django.contrib import admin
from django.urls import path
from first_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('index.html', views.index, name='index_html'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('contact/', views.contact, name='contact'),
    #chi tiết sản phẩm
    path('product/<str:product_code>/', views.product_detail, name='product_detail'),
    #danh mục sản phẩm
    path('category/<str:category_id>/', views.category_products, name='category_products'),
    #table
    path('print-qr/<int:table_id>/', views.print_qr, name='print_qr'),
    path('table/<int:table_id>/', views.table_order, name='table_order'),
    #order

    #giỏ hàng
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<str:product_code>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:product_code>/', views.remove_from_cart, name='remove_from_cart'),
    #thanh toán
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_DIR)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)