# admin.py
from django.conf import settings
from django.contrib import admin
from django.core.files.base import ContentFile
from django.forms import BaseInlineFormSet
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
from django.db.models import Sum
from first_app.services.inventory_service import InventoryService
from django.db import transaction

from django.core.exceptions import ValidationError
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
    readonly_fields = ('material', 'quantity', 'created_at', 'po_id')
    fields = ('material', 'quantity', 'created_at', 'po_id')
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
    list_display = ('stockin_id', 'po', 'created_at')
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

@admin.register(StatusMaster)
class StatusMasterAdmin(admin.ModelAdmin):
    list_display = ('status_code', 'status_name')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')

@admin.register(ProductMaterial)
class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ('product', 'material', 'quantity_required')

@admin.register(ProductMaster)
class ProductMasterAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'description', 'price', 'is_active', 'update_by', 'update_time', 'total_sold')
    # def display_abc(self, obj):
    #     return obj.product_code
    # # Đây là nơi bạn đổi tên hiển thị trên cột
    # display_abc.short_description = 'abc'
    # # (Tùy chọn) Cho phép nhấn vào để sắp xếp theo product_code
    # display_abc.admin_order_field = 'product_code'

    def total_sold(self, obj):
        total = OrderDetail.objects.filter(product=obj).aggregate(total=Sum('quantity'))['total']
        return total or None
    total_sold.short_description = 'Đã bán'

class OrderDetailInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_product = False
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            product = form.cleaned_data.get("product")
            quantity = form.cleaned_data.get("quantity")

            if not product:
                raise ValidationError("Bạn phải chọn sản phẩm.")
            if not quantity or quantity <= 0:
                raise ValidationError("Số lượng phải lớn hơn 0.")

            has_product = True

        if not has_product:
            raise ValidationError("Đơn hàng phải có ít nhất 1 sản phẩm.")

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 1
    formset = OrderDetailInlineFormSet
    can_delete = True
    def get_fields(self, request, obj=None):
        return ('product', 'quantity')

    def customer_name(self, obj):
        return obj.order.customer.customer_name if obj.order and obj.order.customer else "Trống"
    customer_name.short_description = "Tên khách hàng"

    def customer_phone(self, obj):
        return obj.order.customer.phone if obj.order and obj.order.customer else "Trống"
    customer_phone.short_description = "SĐT"

    def customer_address(self, obj):
        return obj.order.customer.address if obj.order and obj.order.customer else "Trống"
    customer_address.short_description = "Địa chỉ"

class PaymentStatusFilter(admin.SimpleListFilter):
    title = 'Chọn Trạng Thái Thanh Toán'
    parameter_name = 'payment_status'
    def lookups(self, request, model_admin):
        return (
            ('paid', 'Đã thanh toán'),
            ('unpaid', 'Chưa thanh toán'),
        )
    def queryset(self, request, queryset):
        if self.value() == 'paid':
            return queryset.filter(status__status_code=2)
        if self.value() == 'unpaid':
            return queryset.filter(status__status_code=1)
        return queryset

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'orderId', 'partnerCode', 'amount', 'orderInfo', 'created_at', 'status', 'table', 'qr_code', 'note')
    actions = ['updatestatus', 'destroyorder', 'print_qr_action']
    inlines = [OrderDetailInline]
    change_form_template = "admin/first_app/order/change_form.html"
    list_filter = ('table',PaymentStatusFilter,)

    def get_model_perms(self, request):

        perms = super().get_model_perms(request)
        if not request.user.has_perm("first_app.view_order"):
            return {}
        return perms
    def note(self, obj):
       if obj.customer and obj.customer.note:
           return obj.customer.note
       return "Không có ghi chú"
    note.short_description = 'Ghi chú'

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return [
                ('Nhập thông tin', {
                    'fields': ('orderId','table')
                }),
            ]
        return []

    def save_model(self, request, obj, form, change):
        if not obj.partnerCode:
            obj.partnerCode = "Đơn hàng của nhân viên"
        if obj.amount is None:
            obj.amount = 0
        if not obj.orderInfo:
            obj.orderInfo = "Nhận tại cửa hàng"
        if not obj.status:
            first_status = StatusMaster.objects.order_by('status_code').first()
            obj.status = first_status
        super().save_model(request, obj, form, change)
        if not obj.qr_code:
            qr_url = f"{settings.NGROK_URL}/order-detail/{obj.orderId}/"
            qr_file = TableServices.generate_qr_for_order(qr_url)
            obj.qr_code.save(
                f"{obj.orderId}.png",
                qr_file,
                save=True
            )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        order = form.instance
        total_bill = 0
        details = order.orderdetail_set.all()
        for detail in details:
            detail.totalPrice = detail.product.price * detail.quantity
            total_bill += detail.totalPrice
            detail.save(update_fields=['totalPrice'])
        # Cập nhật tổng tiền cho Order
        order.amount = total_bill
        order.save(update_fields=['amount'])

    def has_add_permission(self, request):
        return True
    def has_change_permission(self, request, obj=None):
        return True
    @admin.action(description="Đã thanh toán")
    def updatestatus(self, request, queryset):
        paid_status = StatusMaster.objects.filter(status_code=2).first()
        if not paid_status:
            self.message_user(request, "Lỗi: Chưa cấu hình status_code = 2", level='error')
            return
        updated_count = 0
        for order in queryset:
            # CHỈ xử lý những đơn đang ở trạng thái Chờ (code 1)
            if order.status and order.status.status_code == 1:
                order.status = paid_status
                order.save()
                InventoryService.reduce_inventory(order)
                updated_count += 1
        if updated_count == 0:
            self.message_user(request, "Không có đơn hàng nào hợp lệ để thanh toán (Phải ở trạng thái Chờ).",level='warning')
        else:
            self.message_user(request, f"Đã xác nhận thanh toán và trừ tồn kho cho {updated_count} đơn hàng.")

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
#
# def custom_admin_index(request, extra_context=None):
#     # Không phải superuser → KHÔNG xem dashboard
#     if not request.user.is_superuser:
#         # redirect về admin index mặc định (không dashboard)
#         return _original_index(request)
#
#     #Superuser → dashboard
#     extra_context = extra_context or {}
#     today = date.today()
#
#     chart_data = DashboardService.get_daily_revenue(
#         month=today.month,
#         year=today.year
#     )
#     summary = DashboardService.get_summary()
#     order_status_data = DashboardService.get_order_status_data()
#     today_revenue = DashboardService.get_today_revenue()
#     top_products = DashboardService.get_top_selling_products(limit=5)
#
#     extra_context.update({
#         "chart_data": chart_data,
#         "order_status_data": order_status_data,
#         **summary,
#         "top_products": top_products,
#         "today_revenue": today_revenue,
#     })
#     context = dict(admin.site.each_context(request), **extra_context)
#     return TemplateResponse(request, "admin/index.html", context)
#
# admin.site.index = custom_admin_index

