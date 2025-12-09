import hashlib
import hmac
import json
import re
from datetime import timezone

from django.conf import settings
from django.core.signing import BadSignature
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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from first_app.services.payment import MomoService

from first_app.models import Order

from first_app.services.orderdetail_services import NotificationService

from first_app.models import OrderDetail

from first_app.services.deliveryorder import DeliveryService
from first_app.services.sendemail import send_order_email
from first_app.models import Customer

from first_app.services.base_services import SearchService

from first_app.services.inventory_service import InventoryService


from first_app.services.inpdf import generate_invoice

from first_app.models import Supplier, Material

from first_app.services.purchase_order_service import PurchaseOrderService
from first_app.models import PurchaseOrder
from itsdangerous import URLSafeSerializer


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
def product_detail(request, product_code):#hiển thị trang chi tiết sản phẩm
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
def print_qr(request, table_id): #in QR bàn
    buffer = TableServices.generate_qr_for_table(table_id, request)
    return HttpResponse(buffer, content_type="image/png")

def order_detail_qr(request, order_id):
    # Lấy order theo orderId
    order = get_object_or_404(Order, orderId=order_id)
    order_details = order.orderdetail_set.all()
    return render(request, 'orderdetail.html', {
        'order': order,
        'order_details': order_details,

    })


def table_order(request, table_id):
    # Lưu table_id vào session để biết khách đang ngồi ở bàn nào
    request.session['table_id'] = table_id
    # Nếu session chưa có order_key, tạo một mã duy nhất (UUID) cho đơn hàng
    # order_key giúp phân biệt các phiên đặt món khác nhau
    if 'order_key' not in request.session:
        request.session['order_key'] = str(uuid.uuid4())
        # Lấy order_key từ session để truyền vào template
    order_key = request.session['order_key']
    # Lấy danh sách sản phẩm (thực đơn) đang hoạt động từ service
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


#orderdetail
def get_notifications(request): #lấy thông tin hiện detail lên thông báo
    notifications = NotificationService.get_recent_notifications(request)
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
            if result_code == "0":
                paid_status = StatusMaster.objects.filter(status_code=2).first()
                if paid_status:
                    order.status = paid_status
                    order.save()
                    InventoryService.reduce_inventory(order)
                    messages.success(request, "💰 Thanh toán thành công!")
            else:
                failed_status = StatusMaster.objects.filter(status_code=3).first()
                if failed_status:
                    order.status = failed_status
                    order.save()
                messages.warning(request, f"⚠️ Thanh toán thất bại hoặc bị hủy ({request.GET.get('message')})")
        except Order.DoesNotExist:
            messages.error(request, "Không tìm thấy đơn hàng.")
    # 👉 Sau khi xử lý xong, quay lại trang chủ (index)
    return redirect("index")
@csrf_exempt
def momo_ipn(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)
    data = json.loads(request.body.decode('utf-8'))
    print(" IPN nhận từ MoMo:", data)

    order_id = data.get("orderId")
    result_code = data.get("resultCode")
    amount = data.get("amount")

    # Tạo chuỗi để xác minh chữ ký
    raw_signature = (
        f"accessKey={MomoService.ACCESS_KEY}&amount={amount}&extraData={data.get('extraData','')}"
        f"&message={data.get('message','')}&orderId={order_id}&orderInfo={data.get('orderInfo','')}"
        f"&orderType={data.get('orderType','')}&partnerCode={data.get('partnerCode','')}"
        f"&payType={data.get('payType','')}&requestId={data.get('requestId','')}"
        f"&responseTime={data.get('responseTime','')}&resultCode={result_code}"
        f"&transId={data.get('transId','')}"
    )
    generated_signature = hmac.new(
        MomoService.SECRET_KEY.encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    if generated_signature != data.get("signature"):
        return JsonResponse({"message": "Invalid signature"}, status=400)
    try:
        order = Order.objects.get(orderId=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"message": "Order not found"}, status=404)
    # Nếu thanh toán thành công
    if result_code == 0:
        success_status = StatusMaster.objects.filter(status_code=2).first()
        order.status = success_status
        order.save()
        InventoryService.reduce_inventory(order)
        # --- Gửi email tại đây ---
        customer = order.customer
        if customer and customer.email:
            send_order_email(customer.email, order)
        return JsonResponse({"message": "Payment success", "resultCode": 0})
    else:
        failed_status = StatusMaster.objects.filter(status_code=3).first()  # 3 = Thanh toán thất bại
        order.status = failed_status
        order.save()
        return JsonResponse({"message": "Payment failed", "resultCode": result_code})

#lấy thông tin hiện lên form
def delivery_info(request):
    products, grand_total = DeliveryService.get_delivery_page(request.session)
    context = {
        'products': products,
        'grand_total': grand_total,
    }
    return render(request, 'infororder.html', context)


def place_order(request):
    if request.method == "POST":
        name = request.POST.get("customer_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        email = request.POST.get("email")
        note = request.POST.get("note")
        payment_method = request.POST.get("payment_method")
        order_type = request.POST.get("order_type")
        # --- Kiểm tra số điện thoại ---
        if not re.match(r"^0[0-9]{9,10}$", phone):
            return JsonResponse({"error": "Số điện thoại không hợp lệ."}, status=400)
        # --- Kiểm tra email ---
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"error": "Email không hợp lệ."}, status=400)
        # --- Lưu hoặc tạo Customer ---
        customer, created = Customer.objects.get_or_create(
            phone=phone,
            defaults={
                "customer_name": name,
                "email": email,
                "address": address,
                "note": note,
            }
        )
        # Nếu khách hàng đã tồn tại -> cập nhật lại thông tin
        if not created:
            customer.customer_name = name
            customer.email = email
            customer.address = address
            customer.note = note
            customer.save()
        if order_type == "pickup":
            order_info = f"Nhận tại cửa hàng"
        else:
            order_info = f"Đặt hàng giao tận nơi"
        # --- Gọi phương thức thanh toán tương ứng ---
        if payment_method == "COD":
            order = MomoService.pay_cash(request, order_info, customer)
            if email and order:
                InventoryService.reduce_inventory(order)
                send_order_email(email, order)
            messages.success(request, " Đặt hàng thành công! Cảm ơn bạn đã mua hàng")
            return redirect("portfolio")
        elif payment_method == "MOMO":
           #return luôn redirect
            return MomoService.create_order_from_cart(request, order_info, customer)
        else:
            return JsonResponse({"error": "Phương thức thanh toán không hợp lệ."})
    return redirect("delivery_info")


def search_products_view(request):
    query = request.GET.get('q', '')
    products = SearchService.search_products(query)

    context = {
        'products': products,
        'query': query
    }
    return render(request, 'search_results.html', context)
#xuất hóa đơn
def export_invoice(request, pk):
    order = get_object_or_404(Order, pk=pk)
    details = OrderDetail.objects.filter(order=order)

    pdf_content = generate_invoice(order, details)
    if not pdf_content:
        return HttpResponse("Lỗi tạo PDF", status=500)

    # filename dùng order.orderId nếu bạn muốn mã uuid, hoặc order.id
    filename = f"invoice_{order.orderId if hasattr(order,'orderId') else order.pk}.pdf"

    response = HttpResponse(pdf_content, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

#form nhập tồn kho

def nhap_ton_kho(request):
    materials = Material.objects.all()
    suppliers = Supplier.objects.all()
    purchase_orders = PurchaseOrder.objects.filter(status__status_code=7)  # PO đã chấp nhận NCC

    if request.method == "POST":
        po_id = request.POST.get("po_id")
        supplier_id = request.POST.get("supplier")
        items = []

        for material in materials:
            qty_str = request.POST.get(f"qty_{material.material_id}")
            try:
                qty = float(qty_str)
            except (TypeError, ValueError):
                qty = 0
            if qty > 0:
                items.append({
                    "material_id": material.material_id,
                    "quantity": qty
                })

        if items:
            stockin = InventoryService.create_stockin(supplier_id, items, po_id=po_id)
            messages.success(request, f"Đã nhập {len(items)} nguyên liệu vào tồn kho.")
        else:
            messages.warning(request, "Không có nguyên liệu nào để nhập.")

        return redirect("/admin/first_app/inventory/")

    return render(request, "admin/nhap_ton_kho.html", {
        "materials": materials,
        "suppliers": suppliers,
        "purchase_orders": purchase_orders
    })
#nhà cung cấp
def dat_don_hang(request):
    """
    Cửa hàng tạo PO chờ NCC nhận (không gán supplier ngay)
    Cho phép order bất kỳ số lượng nguyên liệu nào > 0.
    """
    materials = Material.objects.all()

    if request.method == "POST":
        note = request.POST.get("note", "")
        items = []

        for m in materials:
            qty_str = request.POST.get(f"qty_{m.material_id}")
            try:
                qty = float(qty_str)
            except (TypeError, ValueError):
                qty = 0
            if qty > 0:
                items.append({
                    "material_id": m.material_id,
                    "quantity": qty
                })

        if items:
            # Tạo PO chờ NCC nhận, supplier=None
            po = PurchaseOrderService.create_purchase_order_waiting(items, note)
            messages.success(
                request,
                f"Đã tạo PO {po.po_id} với {len(items)} nguyên liệu. Nhà cung cấp sẽ nhận đơn và gửi thông báo sau."
            )
        else:
            messages.warning(request, "Không có nguyên liệu nào được chọn.")

        return redirect("/datdonhang/")  # quay lại trang đặt đơn

    return render(request, "admin/dat_don_hang.html", {
        "materials": materials
    })

#xác nhận từ củaư hàng gửi email về
def confirm_purchase_order_view(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    # Nếu PO chưa có NCC, gán NCC đang đăng nhập
    if po.supplier is None:
        po.supplier = request.user.profile
        po.save()
    try:
        PurchaseOrderService.confirm_purchase_order(po)
        messages.success(request, f"Đơn hàng PO {po.po_id} đã xác nhận. Email đã gửi về cửa hàng.")
    except Exception as e:
        messages.error(request, f"Lỗi khi xác nhận đơn hàng: {e}")
    return redirect('/admin/first_app/purchaseorder/')

#xử lý link chấp nhận từ chối của cửa hàng đối với ncc
def po_accept(request, token):
    s = URLSafeSerializer(settings.SECRET_KEY)
    try:
        data = s.loads(token)
        po_id = data['po_id']
    except BadSignature:
        return HttpResponse("Link không hợp lệ!", status=400)

    po = get_object_or_404(PurchaseOrder, po_id=po_id)
    status_accepted = StatusMaster.objects.filter(status_code=7).first()  # Trạng thái 7: Chấp nhận NCC
    if status_accepted:
        po.status = status_accepted
        po.save()
    return redirect('/admin/first_app/purchaseorder/')  # hoặc page thông báo

def po_reject(request, token):
    s = URLSafeSerializer(settings.SECRET_KEY)
    try:
        data = s.loads(token)
        po_id = data['po_id']
    except BadSignature:
        return HttpResponse("Link không hợp lệ!", status=400)

    po = get_object_or_404(PurchaseOrder, po_id=po_id)
    status_rejected = StatusMaster.objects.filter(status_code=3).first()  # Trạng thái 3: từ chối NCC
    if status_rejected:
        po.status = status_rejected
        po.save()
    return redirect('/admin/first_app/purchaseorder/')
