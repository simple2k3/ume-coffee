from django.core.mail import send_mail
from first_app.models import OrderDetail
def send_order_email(to_email, order):
    # Lấy danh sách sản phẩm trong đơn hàng
    order_details = OrderDetail.objects.filter(order=order)
    product_lines = ""
    for item in order_details:
        product_lines += f"- {item.product.product_name} (SL: {item.quantity}) - {item.totalPrice:,} VND\n"
    subject = f"Xác nhận đơn hàng #{order.orderId}"
    message = f"""
Xin chào {order.customer.customer_name},
Cảm ơn bạn đã đặt hàng tại Ume Coffee!
Mã đơn hàng: {order.orderId}
Tổng tiền: {order.amount:,} VND
Hình thức nhận hàng: {order.orderInfo}
Danh sách sản phẩm:
{product_lines}
Chúng tôi sẽ sớm chuẩn bị đơn hàng cho bạn.
Trân trọng,
Ume Coffee
"""
    send_mail(subject, message, "noreply@umecoffee.vn", [to_email])
