# admin.py
from django.contrib import admin
from django.http import HttpResponse
import zipfile
from io import BytesIO
import os
from decouple import config  # pip install python-decouple

from first_app.models import TableMaster
from first_app.services.qr_table_services import TableServices

NGROK_URL = config('NGROK_URL')


@admin.register(TableMaster)
class TableMasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_name')
    actions = ['print_qr_action']

    def print_qr_action(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "Chưa chọn bàn nào!")
            return

        if queryset.count() == 1:
            table = queryset.first()
            url = f"{NGROK_URL}/table/{table.id}/"
            buffer = TableServices.generate_qr_for_table(url)
            return HttpResponse(buffer, content_type='image/png')

        # Nếu nhiều bàn -> tạo zip QR code
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for table in queryset:
                url = f"{NGROK_URL}/table/{table.id}/?format=html"
                img_buffer = TableServices.generate_qr_for_table(url)
                zf.writestr(f'Ban_{table.id}.png', img_buffer.getvalue())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="qr_tables.zip"'
        return response

    print_qr_action.short_description = "In QR cho bàn đã chọn"
