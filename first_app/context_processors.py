
from first_app.services.category_services import CategoriesService
from django.urls import resolve
from django.utils.text import slugify

def categories_processor(request):
    categories_data = CategoriesService.get_all_categories()
    return {'categories_data': categories_data}

def breadcrumbs(request):
    return {
        'breadcrumbs': getattr(request, 'breadcrumbs', [])
    }