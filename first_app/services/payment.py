import hashlib
import hmac
import json
import os
import uuid
import requests
import json
from datetime import timezone

from django.conf import settings
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

from first_app.models import Order

from first_app.services.orderdetail_services import NotificationService
from first_app.services.sendemail import send_order_email
from first_app.models import OrderDetail

NGROK_URL = os.environ.get("NGROK_URL")
class MomoService:
    # Cấu hình MoMo sandbox
    ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create"
    PARTNER_CODE = "MOMO"
    ACCESS_KEY = "F8BBA842ECF85"
    SECRET_KEY = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    REQUEST_TYPE = "captureWallet"

    REDIRECT_URL = f"{NGROK_URL}/payment/momo/return/"
    IPN_URL = f"{NGROK_URL}/payment/momo/ipn/"
    #tạo yêu cầu tới momo
    @staticmethod
    def create_payment(amount: int, order_info="Thanh toán UME Coffee", extra_data=""):
        request_id = str(uuid.uuid4())
        order_id = str(uuid.uuid4())
        amount_str = str(amount)
        # Tạo chữ ký
        raw_signature = (
            f"accessKey={MomoService.ACCESS_KEY}&amount={amount_str}&extraData={extra_data}"
            f"&ipnUrl={MomoService.IPN_URL}&orderId={order_id}&orderInfo={order_info}"
            f"&partnerCode={MomoService.PARTNER_CODE}&redirectUrl={MomoService.REDIRECT_URL}"
            f"&requestId={request_id}&requestType={MomoService.REQUEST_TYPE}"
        )
        signature = hmac.new(
            MomoService.SECRET_KEY.encode("utf-8"),
            raw_signature.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        data = {
            "partnerCode": MomoService.PARTNER_CODE,
            "accessKey": MomoService.ACCESS_KEY,
            "requestId": request_id,
            "amount": amount_str,
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": MomoService.REDIRECT_URL,
            "ipnUrl": MomoService.IPN_URL,
            "extraData": extra_data,
            "requestType": MomoService.REQUEST_TYPE,
            "signature": signature,
            "lang": "vi"
        }

        try:
            response = requests.post(MomoService.ENDPOINT, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    @staticmethod
    def create_order_from_cart(request, order_info, customer):
        cart = request.session.get("cart", {})
        table_id = request.session.get('table_id')
        table = TableMaster.objects.filter(id=table_id).first() if table_id else None
        if not isinstance(cart, dict) or not cart:
            return JsonResponse({"error": "Giỏ hàng trống hoặc sai định dạng"})
        total = sum(
            item["price"] * item["quantity"]
            for item in cart.values()
            if isinstance(item, dict) and "price" in item and "quantity" in item
        )
        if total == 0:
            return JsonResponse({"error": "Không có sản phẩm hợp lệ trong giỏ hàng"})
        # --- Gọi API MoMo ---
        momo_result = MomoService.create_payment(total, order_info)
        pay_url = momo_result.get("payUrl")
        if not pay_url:
            return JsonResponse({"error": momo_result})

        pending_status = StatusMaster.objects.filter(status_code=1).first()
        if not pending_status:
            return JsonResponse({"error": "Không tìm thấy trạng thái có mã 1 (Đang Xử Lý)"})

        # --- Tạo Order ---
        order = Order.objects.create(
            partnerCode=momo_result.get("partnerCode", ""),
            requestId=momo_result.get("requestId", ""),
            amount=total,
            orderId=momo_result.get("orderId", ""),
            orderInfo=order_info,
            redirectUrl=momo_result.get("redirectUrl", ""),
            requestType=momo_result.get("requestType", "captureWallet"),
            extraData=momo_result.get("extraData", ""),
            lang=momo_result.get("lang", "vi"),
            signature=momo_result.get("signature", ""),
            status=pending_status,
            table=table,
            customer=customer,
        )
        qr_url = f"{NGROK_URL}/order-detail/{order.orderId}/"
        qr_file = TableServices.generate_qr_for_order(qr_url)
        order.qr_code.save(f"{order.orderId}.png", qr_file, save=True)
        # --- Tạo OrderDetail ---
        for code, item in cart.items():
            try:
                product = ProductMaster.objects.get(product_code=code)
                OrderDetail.objects.create(
                    order=order,
                    product=product,
                    quantity=item.get("quantity", 1),
                    totalPrice=float(item.get("price", 0)) * int(item.get("quantity", 1)),
                    create_at=timezone.now()
                )
            except ProductMaster.DoesNotExist:
                continue

        request.session["orderId"] = order.orderId
        return redirect(pay_url)

    @staticmethod
    def pay_cash(request, order_info, customer):
        cart = request.session.get("cart", {})
        table_id = request.session.get("table_id")
        table = TableMaster.objects.filter(id=table_id).first() if table_id else None

        if not isinstance(cart, dict) or not cart:
            return JsonResponse({"error": "Giỏ hàng trống hoặc sai định dạng"})

        total = sum(
            item["price"] * item["quantity"]
            for item in cart.values()
            if isinstance(item, dict) and "price" in item and "quantity" in item
        )

        pending_status = StatusMaster.objects.filter(status_code=1).first()
        order = Order.objects.create(
            partnerCode="Tiền Mặt",
            requestId=str(uuid.uuid4()),
            amount=total,
            orderId=str(uuid.uuid4()),
            orderInfo=order_info,
            redirectUrl="",
            requestType="cash",
            extraData="",
            lang="vi",
            signature="",
            status=pending_status,
            table=table,
            customer=customer,
        )
        qr_url = f"{NGROK_URL}/order-detail/{order.orderId}/"
        qr_file = TableServices.generate_qr_for_order(qr_url)
        order.qr_code.save(f"{order.orderId}.png", qr_file, save=True)

        for code, item in cart.items():
            try:
                product = ProductMaster.objects.get(product_code=code)
                OrderDetail.objects.create(
                    order=order,
                    product=product,
                    quantity=item.get("quantity", 1),
                    totalPrice=float(item.get("price", 0)) * int(item.get("quantity", 1)),
                    create_at=timezone.now()
                )
            except ProductMaster.DoesNotExist:
                continue
                #xóa khỏi session khi tạo đơn hàng
        request.session["cart"] = {}
        request.session.modified = True
        return order