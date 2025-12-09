# admin.py
from django.contrib import admin
from django.core.files.base import ContentFile
from django.http import HttpResponse
import zipfile
from io import BytesIO
import os
import json
from decouple import config
from django.template.response import TemplateResponse
from first_app.models import TableMaster
from first_app.services.qr_table_services import TableServices
from first_app.models import Categories
from first_app.models import StatusMaster

from first_app.models import ProductMaster

from first_app.models import Order

from first_app.models import OrderDetail

from first_app.models import Customer

from first_app.services.dashbroad import DashboardService
from datetime import date

from first_app.models import Inventory

from first_app.models import ProductMaterial
from first_app.models import Material

from first_app.models import Supplier
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from first_app.models import StockIn
from first_app.models import StockInDetail
from first_app.models import PurchaseOrderDetail
from first_app.models import PurchaseOrder
NGROK_URL = config('NGROK_URL')

class MyAdminSite(admin.AdminSite):
    site_header = "Trang quản trị hệ thống"
    site_title = "Quản trị"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        stats = DashboardService.get_order_stats(months=6)
        extra_context["chart_data"] = stats
        return TemplateResponse(request, "admin/index.html", extra_context)

class SupplierInline(admin.StackedInline):
    model = Supplier
    can_delete = False
    verbose_name_plural = 'Thông tin nhà cung cấp'
# Custom UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (SupplierInline,)
# Hủy đăng ký User mặc định và đăng ký lại với UserAdmin mới
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

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

class StockInDetailInline(admin.TabularInline):
    model = StockInDetail
    extra = 0
    can_delete = False
    readonly_fields = ('material', 'quantity', 'created_at', 'supplier_name', 'po_id')
    fields = ('material', 'quantity', 'created_at', 'supplier_name', 'po_id')
    verbose_name = "Chi tiết nhập kho"
    verbose_name_plural = "Danh sách chi tiết nhập kho"

    def supplier_name(self, obj):
        if obj.stockin and obj.stockin.supplier:
            return obj.stockin.supplier.user.username if obj.stockin.supplier.user else "-"
        return "-"
    supplier_name.short_description = "Nhà cung cấp"

    def po_id(self, obj):
        if obj.stockin and obj.stockin.po:
            return obj.stockin.po.po_id
        return "-"
    po_id.short_description = "PO ID"

@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display = ('stockin_id', 'po', 'supplier', 'created_at')
    inlines = [StockInDetailInline]
    # Không hiển thị field StockIn "General"
    def get_fieldsets(self, request, obj=None):
        return []
    # Chỉ xem, không cho sửa StockIn
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class PurchaseOrderDetailInline(admin.TabularInline):
    model = PurchaseOrderDetail
    extra = 0
    readonly_fields = ('material', 'quantity')
    can_delete = False

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_id', 'supplier', 'status', 'created_at')
    inlines = [PurchaseOrderDetailInline]
    change_form_template = "admin/first_app/purchaseorder/change_form.html"

    def has_change_permission(self, request, obj=None):
        return False  # nếu chỉ muốn xem, không chỉnh sửa
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('material', 'quantity', 'min_quantity', 'updated_at')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'material_name', 'unit')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')

@admin.register(ProductMaterial)
class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ('product', 'material', 'quantity_required')

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
    def get_fieldsets(self, request, obj=None):
        return []
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request):
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
_original_index = admin.site.index
def custom_admin_index(request, extra_context=None):
    extra_context = extra_context or {}
    today = date.today()
    # Biểu đồ doanh thu trong tháng hiện tại
    chart_data = DashboardService.get_daily_revenue(month=today.month, year=today.year)
    # Thống kê tổng quan
    summary = DashboardService.get_summary()
    # Trạng thái đơn hàng
    order_status_data = DashboardService.get_order_status_data()
    # Tổng doanh thu hôm nay
    today_revenue = DashboardService.get_today_revenue()
    top_products = DashboardService.get_top_selling_products(limit=5)
    # Gộp vào context
    extra_context.update({
        "chart_data": chart_data,
        "order_status_data": order_status_data,
        **summary,
        "top_products": top_products,
        "today_revenue": today_revenue,
        "current_month_label": today.strftime("Tháng %m/%Y"),
    })

    context = dict(admin.site.each_context(request), **extra_context)
    return TemplateResponse(request, "admin/index.html", context)

#  Ghi đè trang index mặc định
admin.site.index = custom_admin_index