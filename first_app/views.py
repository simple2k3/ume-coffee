import json
from datetime import timezone

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import uuid

from django.views.decorators.csrf import csrf_exempt
from first_app.services.product_services import ProductsServices
from first_app.services.qr_table_services import TableServices
from first_app.models import ProductMaster
from first_app.services.category_services import CategoriesService
from first_app.services.cart_services import CartService
from first_app.models import Categories
from first_app.utils.breadcrumbs import register_breadcrumb
from first_app.models import TableMaster
from first_app.models import StatusMaster
from django.contrib import messages
from django.utils import timezone

from first_app.services.payment import MomoService

from first_app.models import Order

from first_app.services.orderdetail_services import NotificationService

from first_app.models import OrderDetail


#trang chủ
def index(request):
    return render(request, 'index.html')
#trang liên hệ
def contact(request):
    return render(request, 'contact.html')

#trang sản phẩm
@register_breadcrumb('Sản Phẩm')
def portfolio(request):
    table_id = request.session.get('table_id')
    if not table_id:
        messages.error(request, "Vui lòng quét QR bàn trước khi xem sản phẩm.")
        return redirect('index')
    categories = CategoriesService.get_all_categories(limit=6)
    product_data = []
    for c in categories:
        products = ProductMaster.objects.filter(category=c.categories_id)
        product_data.append({
            'categories_id': c.categories_id,
            'category_name': c.categories_name,
            'imageUrl': c.imageUrl,
            'products': products
        })
    return render(request, 'portfolio.html', {'product_data': product_data, 'table_id': table_id})


@register_breadcrumb('Danh Mục')
def product_detail(request, product_code):
    table_id = request.session.get('table_id')
    if not table_id:
        messages.error(request, "Vui lòng quét QR bàn trước khi xem sản phẩm.")
        return redirect('index')

    product = get_object_or_404(ProductMaster, product_code=product_code)
    suggested_products = ProductMaster.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(product_code=product.product_code)[:4]
    return render(request, 'portfolio-details.html', {
        'product': product,
        'suggested_products': suggested_products,
        'table_id': table_id
    })

#table
def print_qr(request, table_id):
    buffer = TableServices.generate_qr_for_table(table_id, request)
    return HttpResponse(buffer, content_type="image/png")

def table_order(request, table_id):
    request.session['table_id'] = table_id
    if 'order_key' not in request.session:
        request.session['order_key'] = str(uuid.uuid4())
    order_key = request.session['order_key']
    product_data = ProductsServices.getlistproduct()
    return render(request, 'index.html', {
        'table_id': table_id,
        'order_key': order_key,
        'product_data': product_data,
    })

#categories
@register_breadcrumb('Chi tiết sản phẩm')
def category_products(request, category_id):
    table_id = request.session.get('table_id')
    if not table_id:
        messages.error(request, "Vui lòng quét QR bàn trước khi xem danh mục.")
        return redirect('index')
    category, products = CategoriesService.get_products_by_category(category_id)
    return render(request, 'Categories_product.html', {
        'category': category,
        'products': products,
        'table_id': table_id
    })

#order

#giỏ hàng
def cart_view(request):
    cart, total_price = CartService.get_cart(request.session)
    table_id = request.session.get('table_id')
    products_list = []
    for code, item in cart.items():
        products_list.append({
            'product_code': code,
            'product_name': item.get('name', ''),
            'base_price': item.get('price', 0),
            'quantity': item.get('quantity', 1),
            'total_price': item.get('price', 0) * item.get('quantity', 1),
            'imageUrl': item.get('imageUrl')
        })

    return render(request, 'cart.html', {
        'products': products_list,
        'total_price': total_price,
        'table_id': table_id,
    })

def update_quantity_view(request, product_code):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        CartService.update_quantity(request.session, product_code, quantity)
    return redirect('cart')

def add_to_cart_view(request, product_code):
    table_id = request.session.get('table_id')
    if not table_id:
        messages.error(request, "Vui lòng quét QR bàn trước khi thêm sản phẩm.")
        return redirect('index')
    product = get_object_or_404(ProductMaster, product_code=product_code)
    CartService.add_to_cart(
        request.session,
        product_code,
        name=product.product_name,
        price=product.price,
        imageUrl=product.imageUrl,
        quantity=1
    )

    messages.success(request, f"Đã thêm {product.product_name} vào giỏ hàng.")
    return redirect(request.META.get('HTTP_REFERER', '/'))



def remove_from_cart(request, product_code):
    CartService.remove_from_cart(request.session, product_code)
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def clear_cart(request):
    CartService.clear_cart(request.session)
    messages.success(request, "Đã xóa toàn bộ giỏ hàng.")
    return redirect('cart_view')

#orderdetail

def get_notifications(request):
    table_id = request.session.get("table_id", "Không rõ bàn")
    notifications = NotificationService.get_recent_notifications(limit=5)

    # Gắn thêm thông tin bàn cho từng thông báo
    for n in notifications:
        n["table_id"] = table_id

    return JsonResponse({'notifications': notifications})

#payment

def momo_payment(request):
    return MomoService.create_order_from_cart(request)

def pay_cash_view(request):
    if request.method == "POST":
        return MomoService.pay_cash(request)
    return JsonResponse({"error": "Phương thức không hợp lệ. Vui lòng dùng POST."})

def momo_return(request):
    result_code = request.GET.get("resultCode")
    order_id = request.session.get("orderId")

    if order_id:
        try:
            order = Order.objects.get(orderId=order_id)
            order.status = "paid" if result_code == "0" else "failed"
            order.save()
        except Order.DoesNotExist:
            pass

    msg = "Thanh toán thành công!" if result_code == "0" else f"Thanh toán thất bại hoặc bị hủy ({request.GET.get('message')})"
    return JsonResponse({"message": msg, "data": request.GET})

@csrf_exempt
def momo_ipn(request):
    #MoMo gửi POST JSON khi thanh toán hoàn tất (IPN callback).
    if request.method == "POST":
        data = json.loads(request.body)
        print(" IPN CALLBACK:", data)
        return JsonResponse({"message": "IPN received successfully"})
    return JsonResponse({"message": "Invalid request"}, status=400)





