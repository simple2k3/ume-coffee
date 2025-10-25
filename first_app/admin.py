# admin.py
from django.contrib import admin
from django.core.files.base import ContentFile
from django.http import HttpResponse
import zipfile
from io import BytesIO
import os
from decouple import config  # pip install python-decouple
from first_app.models import TableMaster
from first_app.services.qr_table_services import TableServices
from first_app.models import Categories
from first_app.models import StatusMaster

from first_app.models import ProductMaster

NGROK_URL = config('NGROK_URL')


@admin.register(TableMaster)
class TableMasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_name', 'qr_code')
    actions = ['print_qr_action']

    def print_qr_action(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "Chưa chọn bàn nào")
            return
        if queryset.count() == 1:
            table = queryset.first()
            url = f"{NGROK_URL}/table/{table.id}/"
            buffer = TableServices.generate_qr_for_table(url)
            file_name = f'table_{table.id}.png'
            table.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=True)
            self.message_user(request, f"Đã tạo QR cho {queryset.count()} bàn")
        # zip_buffer = BytesIO()
        # with zipfile.ZipFile(zip_buffer, 'w') as zf:
        #     for table in queryset:
        #         url = f"{NGROK_URL}/table/{table.id}/?format=html"
        #         img_buffer = TableServices.generate_qr_for_table(url)
        #         zf.writestr(f'Ban_{table.id}.png', img_buffer.getvalue())
        # zip_buffer.seek(0)
        # response = HttpResponse(zip_buffer, content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename="qr_tables.zip"'
        # return response
    print_qr_action.short_description = "In QR cho bàn đã chọn"


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('categories_id', 'categories_name', 'imageUrl')

@admin.register(ProductMaster)
class ProductMasterAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'description', 'price', 'is_active', 'update_by', 'update_time')

