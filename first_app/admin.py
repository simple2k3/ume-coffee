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

from first_app.models import Order

from first_app.models import OrderDetail

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
    print_qr_action.short_description = "In QR cho bàn đã chọn"


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('categories_id', 'categories_name', 'imageUrl')

@admin.register(ProductMaster)
class ProductMasterAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'description', 'price', 'is_active', 'update_by', 'update_time')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('partnerCode', 'amount', 'orderInfo', 'created_at', 'status', 'table')
    actions = ['updatestatus', 'destroyorder']
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    @admin.action(description="Đã thanh toán")
    def updatestatus(self, request, queryset):
        paid_status = StatusMaster.objects.filter(status_code=2).first()
        if not paid_status:
            self.message_user(request, "Không tìm thấy trạng thái có status_code = 2 trong bảng StatusMaster.",level='error')
            return
        updated = 0
        for order in queryset:
            if order.status and order.status.status_code == 1:
                order.status = paid_status
                order.save()
                updated += 1
        if updated == 0:
            self.message_user(request, "Không thể thanh toán đơn hàng",level='warning')
        else:
            self.message_user(request,f"Đã cập nhật {updated} đơn hàng,đơn hàng đã được bạn thanh toán ")

    @admin.action(description="Hủy đơn hàng")
    def destroyorder(self, request, queryset):
        canceled_status = StatusMaster.objects.filter(status_code=3).first()  # 3 = hủy sau khi hủy
        if not canceled_status:
            self.message_user(request, "Không tìm thấy trạng thái có status_code = 3 trong bảng StatusMaster.",level='error')
            return
        updated = 0
        tables_to_clear = set()
        for order in queryset:#hủy đơn hàng có trạng thái 1
            if order.status and order.status.status_code == 1:
                order.status = canceled_status
                order.save()
                updated += 1
                if order.table:
                    tables_to_clear.add(order.table.id)

        # Xóa session giỏ hàng của các bàn đã hủy
        for table_id in tables_to_clear:
            carts = request.session.get('carts', {})
            if str(table_id) in carts:
                del carts[str(table_id)]
            request.session['carts'] = carts

        request.session.modified = True
        if updated == 0:
            self.message_user(request, "Không thể hủy đơn hàng ", level='warning')
        else:
            self.message_user(request,
                              f"Đã hủy {updated} đơn hàng")
@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'totalPrice', 'quantity', 'create_at')

@admin.register(StatusMaster)
class StatusMasterAdmin(admin.ModelAdmin):
    list_display = ('status_code', 'status_name', 'update_by', 'update_time')