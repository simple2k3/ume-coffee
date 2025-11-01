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

from first_app.models import Customer

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

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    can_delete = False
    readonly_fields = ('product','quantity','totalPrice', 'create_at','customer_name','customer_phone','customer_address',)
    fields = ('product','quantity','totalPrice','create_at','customer_name','customer_phone','customer_address',)
    verbose_name = "Chi tiết sản phẩm"
    verbose_name_plural = "Danh sách sản phẩm trong đơn hàng"

    def customer_name(self, obj):
        return obj.order.customer.customer_name if obj.order and obj.order.customer else "-"
    customer_name.short_description = "Tên khách hàng"

    def customer_phone(self, obj):
        return obj.order.customer.phone if obj.order and obj.order.customer else "-"
    customer_phone.short_description = "SĐT"

    def customer_address(self, obj):
        return obj.order.customer.address if obj.order and obj.order.customer else "-"
    customer_address.short_description = "Địa chỉ"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'orderId', 'partnerCode', 'amount', 'orderInfo', 'created_at', 'status', 'table', 'customer', 'qr_code')
    actions = ['updatestatus', 'destroyorder', 'print_qr_action']
    inlines = [OrderDetailInline]
    change_form_template = "admin/first_app/order/change_form.html"

    def print_qr_action(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, " Chưa chọn đơn hàng nào.")
            return
        for order in queryset:
            url = f"{NGROK_URL}/order-detail/{order.orderId}/"
            buffer = TableServices.generate_qr_for_order(url)
            file_name = f'order_{order.id}.png'
            order.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=True)
        self.message_user(request, f"Đã tạo mã QR cho {queryset.count()} đơn hàng.")

    print_qr_action.short_description = " In QR cho đơn hàng đã chọn"
    def get_fieldsets(self, request, obj=None):
        return []
    def has_change_permission(self, request, obj=None):
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

@admin.register(StatusMaster)
class StatusMasterAdmin(admin.ModelAdmin):
    list_display = ('status_code', 'status_name', 'update_by', 'update_time')

@admin.register(Customer)
class CustomerMasterAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'phone', 'address')
