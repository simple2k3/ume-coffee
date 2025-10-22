from django.contrib.sites import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
import uuid
from first_app.services.product_services import CategoriesServices
from django.conf import settings
from first_app.services.qr_table_services import TableServices


def index(request):
    return render(request, 'index.html')
def contact(request):
    return render(request, 'contact.html')


def portfolio(request):
    product_data = CategoriesServices.getlistproduct()
    context = {
        'product_data': product_data
    }
    return render(request, 'portfolio.html', context)



def print_qr(request, table_id):
    buffer = TableServices.generate_qr_for_table(table_id, request)
    return HttpResponse(buffer, content_type="image/png")
def table_order(request, table_id):
    # Mỗi khách quét QR tạo session riêng
    if 'order_key' not in request.session:
        request.session['order_key'] = str(uuid.uuid4())
    order_key = request.session['order_key']

    # Lưu table_id nếu muốn gộp order sau
    request.session['table_id'] = table_id
    product_data = CategoriesServices.getlistproduct()
    # Truyền vào template menu/portfolio
    return render(request, 'index.html', {
        'table_id': table_id,
        'order_key': order_key,
        'product_data': product_data,
    })
# first_app/views.py



def warmup_ngrok(): #gọi mọi static file qua ngrok 1 lần để tunnel sẳn sàn
    try:
        urls = [
            settings.STATIC_URL + "assets/css/main.css",
            settings.STATIC_URL + "assets/vendor/bootstrap/css/bootstrap.min.css",
        ]
        for url in urls:
            requests.get(f"{settings.BASE_NGROK_URL}{url}", timeout=1)
    except Exception:
        pass
