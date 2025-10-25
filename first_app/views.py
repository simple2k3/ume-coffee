from datetime import timezone

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import uuid
from first_app.services.product_services import ProductsServices
from first_app.services.qr_table_services import TableServices
from first_app.models import ProductMaster
from first_app.services.category_services import CategoriesService
from first_app.services.cart_services import CartService
from first_app.models import Categories
from django.contrib import messages
from first_app.utils.breadcrumbs import register_breadcrumb
from first_app.models import TableMaster
from first_app.models import StatusMaster


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
    products, total_price = CartService.get_cart(request.session)
    table_id = request.session.get('table_id')  # Lấy table_id từ session
    return render(request, 'cart.html', {
        'products': products,
        'total_price': total_price,
        'table_id': table_id,  # truyền sang template
    })


def add_to_cart(request, product_code):
    table_id = request.session.get('table_id')
    if not table_id:
        messages.error(request, "Vui lòng quét QR bàn trước khi thêm sản phẩm.")
        return redirect('index')

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        CartService.add_to_cart(request.session, product_code, quantity)
        messages.success(request, f'Đã thêm {quantity} sản phẩm vào giỏ hàng!')
    return redirect(request.META.get('HTTP_REFERER', '/'))

def remove_from_cart(request, product_code):
    table_id = request.session.get('table_id')
    if not table_id:
        messages.error(request, "Vui lòng quét QR bàn trước khi thao tác.")
        return redirect('index')

    CartService.remove_from_cart(request.session, product_code)
    return redirect(request.META.get('HTTP_REFERER', '/'))





