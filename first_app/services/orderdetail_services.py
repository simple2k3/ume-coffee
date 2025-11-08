from first_app.models import Order

class NotificationService:
    @staticmethod
    def get_recent_notifications(request): #hiện thông tin chi tiết đơn hàng của người dùng
        # Lấy danh sách order ID của máy này từ session
        order_ids = request.session.get("orders", [])

        if not order_ids:
            return []
        # Lọc các order theo ID đã lưu trong session, sắp xếp mới nhất trước
        orders = (
            Order.objects
            .select_related('customer', 'status', 'table')
            .filter(id__in=order_ids)
            .order_by('-created_at')
        )

        notifications = []
        for order in orders:
            notifications.append({
                'order_id': order.orderId,
                'customer_name': getattr(order.customer, 'customer_name', ''),
                'address': getattr(order.customer, 'address', ''),
                'amount': order.amount,
            })

        return notifications

    @staticmethod
    def add_order_to_session(request, order_id): #thêm order ID vào session cho máy hiện tại
        orders = request.session.get('orders', [])
        if order_id not in orders:
            orders.append(order_id)
        request.session['orders'] = orders
