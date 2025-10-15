from django.http import HttpResponse
from django.shortcuts import render
from first_app.services.product_services import ProductServices
from first_app.services.category_services import CategoriesServices

def index(request):
    categories_data = CategoriesServices.get_all_categories()
    return render(request, 'index.html', {'categories_data': categories_data})
def portfolio(request):
    product_data = ProductServices.get_all_with_products()
    categories_data = CategoriesServices.get_all_categories()
    context = {
        'product_data': product_data,
        'categories_data': categories_data,
    }
    return render(request, 'portfolio.html', context)
def about(request):
    return render(request, 'about.html')
def contact(request):
    return render(request, 'contact.html')
def portfoliodetails(request):
    return render(request, 'portfolio-details.html')
def show_categories_with_products(request):
    categories_data = CategoriesServices.get_all_with_products()
    return render(request, 'categories.html', {'categories_data': categories_data})

def category_products(request, category_id):
    data = CategoriesServices.get_products_by_category(category_id)
    return render(request, 'category_products.html', data)