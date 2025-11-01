from first_app.models import Order
from django.utils.timezone import localtime

class NotificationService:
    @staticmethod
    def get_recent_notifications(request):
        table_id = request.session.get("table_id")
        if not table_id:
            return []
        orders = (
            Order.objects
            .select_related('customer', 'status', 'table')
            .filter(table_id=table_id)
            .order_by('-created_at')[:1]
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
