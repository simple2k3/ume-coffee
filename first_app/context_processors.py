
from first_app.services.category_services import CategoriesService
from django.urls import resolve
from django.utils.text import slugify

from first_app.services.orderdetail_services import NotificationService


def categories_processor(request):
    categories_data = CategoriesService.get_all_categories()
    return {'categories_data': categories_data}

def breadcrumbs(request):
    return {
        'breadcrumbs': getattr(request, 'breadcrumbs', [])
    }
def notifications_context(request):
    notifications = NotificationService.get_recent_notifications(limit=5)
    return {
        'notifications': notifications,
        'notification_count': len(notifications)
    }