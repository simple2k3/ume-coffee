from first_app.models import OrderDetail
from django.utils.timezone import localtime

class NotificationService:
    @staticmethod
    def get_recent_notifications(limit=5):
        order_details = OrderDetail.objects.select_related('product', 'order').order_by('-create_at').exclude(order__status__status_code=3)[:limit]
        notifications = []

        for item in order_details:
            notifications.append({
                'product_name': item.product.product_name,
                'quantity': item.quantity,
                'status': getattr(item.order, 'status', 'Chờ xử lý'),
                'table_id': getattr(item.order, 'table_id', 'Không rõ bàn'),
                'time': localtime(item.create_at).strftime('%H:%M %d/%m/%Y'),
            })

        return notifications
