
from django.contrib import admin
from django.urls import path, include
from first_app import views
from django.conf import settings
from django.conf.urls.static import static
from first_app.services.payment import MomoService
from first_app.views import export_invoice
from first_app.views import nhap_ton_kho

from first_app.views import dat_don_hang

urlpatterns = [
    #code test
    # path('', views.test, name='test'),
    # path('customers/', views.loadcustomer, name='loadcustomer'),
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
    path('cart/add/<str:product_code>/', views.add_to_cart_view, name='add_to_cart_view'),
    path('cart/remove/<str:product_code>/', views.remove_from_cart, name='remove_from_cart'),

    path('cart/update/<str:product_code>/', views.update_quantity_view, name='update_quantity'),
    #thanh toán
    path('payment/momo/', views.momo_payment, name='momo_payment'),
    path('payment/momo/return/', views.momo_return, name='momo_return'),
    path('payment/momo/ipn/', views.momo_ipn, name='momo_ipn'),
    path("payment/cash/", views.pay_cash_view, name="payment_cash"),

    path('delivery-info/', views.delivery_info, name='delivery_info'),
    path("place-order/", views.place_order, name="place_order"),

    path('order-detail/<str:order_id>/', views.order_detail_qr, name='order_detail'),

    path('search/', views.search_products_view, name='search_products'),

    #xuất hóa đơn
    path('export-invoice/<int:pk>/', export_invoice, name='export_invoice'),
    #nhập tồn kho
    path("nhap-ton-kho/", nhap_ton_kho, name="nhap_ton_kho"),
    #nhập đơn hàng ncc
    path('datdonhang/', dat_don_hang, name='dat_don_hang'),
    #xác nhận đơn hàng từ ncc
    path('purchaseorder/<int:pk>/confirm/', views.confirm_purchase_order_view, name='confirm_purchase_order'),
    #xử lý chấp nhận- hủy đơn từ email
    path('po/accept/<str:token>/', views.po_accept, name='po_accept'),
    path('po/reject/<str:token>/', views.po_reject, name='po_reject'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_DIR)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)