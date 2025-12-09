from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from first_app.models import PurchaseOrder, PurchaseOrderDetail, Supplier, StatusMaster, Material
from itsdangerous import URLSafeSerializer

class PurchaseOrderService:

    @staticmethod
    def create_purchase_order_waiting(items, note=None):
        """
        Cửa hàng tạo PO chờ NCC nhận (supplier=None)
        Gửi email thông báo tất cả NCC có email.
        """
        pending_status = StatusMaster.objects.filter(status_code=1).first()  # Chờ NCC nhận
        po = PurchaseOrder.objects.create(
            supplier=None,
            note=note,
            status=pending_status
        )

        # Tạo chi tiết đơn hàng
        for item in items:
            material = Material.objects.get(pk=item["material_id"])
            qty = float(item["quantity"])
            if qty > 0:
                PurchaseOrderDetail.objects.create(
                    po=po,
                    material=material,
                    quantity=qty
                )

        # Gửi email thông báo NCC
        suppliers = Supplier.objects.filter(user__email__isnull=False)
        subject = f"[Đơn hàng mới] PO {po.po_id}"
        message = f"Bạn có đơn hàng mới từ cửa hàng UME COFFEE!\nPO ID: {po.po_id}\nGhi chú: {po.note}\nChi tiết:\n"
        for detail in po.details.all():
            message += f"- {detail.material.material_name}: {detail.quantity}\n"

        for supplier in suppliers:
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [supplier.user.email])
                print(f"[EMAIL SENT] PO {po.po_id} gửi tới {supplier.user.username}")
            except Exception as e:
                print(f"[EMAIL ERROR] PO {po.po_id} gửi tới {supplier.user.username}: {e}")

        return po

    @staticmethod
    def confirm_purchase_order(po: PurchaseOrder):
        confirmed_status = StatusMaster.objects.filter(status_code=6).first()  # Trạng thái "Đã xác nhận"
        if not confirmed_status:
            raise ValueError("Không tìm thấy trạng thái 'Đã xác nhận'")

        # Cập nhật trạng thái
        po.status = confirmed_status
        po.save()

        # Lấy thông tin nhà cung cấp
        if po.supplier:
            supplier_name = po.supplier.user.username if po.supplier.user else "Chưa có username"
            supplier_email = po.supplier.user.email if po.supplier.user else "Chưa có email"
            supplier_phone = po.supplier.phone or "Chưa có số điện thoại"
            supplier_address = po.supplier.address or "Chưa có địa chỉ"
        else:
            supplier_name = "Chưa có NCC"
            supplier_email = "N/A"
            supplier_phone = "N/A"
            supplier_address = "N/A"

        s = URLSafeSerializer(settings.SECRET_KEY)
        token = s.dumps({'po_id': po.po_id})
        # Tạo link chấp nhận / từ chối
        accept_url = settings.SITE_URL + reverse('po_accept', args=[token])
        reject_url = settings.SITE_URL + reverse('po_reject', args=[token])
        # Tạo nội dung email
        subject = f"[Đơn hàng đã được xác nhận] PO {po.po_id}"
        message = f"""
    Đơn hàng PO {po.po_id} đã được xác nhận.

    Nhà cung cấp: {supplier_name}
    Email NCC: {supplier_email}
    Số điện thoại NCC: {supplier_phone}
    Địa chỉ NCC: {supplier_address}
    Ngày tạo PO: {po.created_at.strftime('%d/%m/%Y %H:%M')}
    Ghi chú: {po.note or 'Không có'}

    Chi tiết đơn hàng:
    """
        for detail in po.details.all():
            message += f"- {detail.material.material_name}: {detail.quantity} {detail.material.unit}\n"
            message += f"""

            Chấp nhận NCC: {accept_url}
            Từ chối NCC: {reject_url}
    """
        # Gửi email cho cửa hàng
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
            print(f"[EMAIL SENT] PO {po.po_id} đã gửi email cho cửa hàng.")
        except Exception as e:
            print(f"[EMAIL ERROR] PO {po.po_id}: {e}")




