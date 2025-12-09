# first_app/services/inventory_service.py
from django.utils import timezone

from django.core.mail import send_mail
from django.conf import settings
from first_app.models import Inventory, ProductMaterial, OrderDetail

from first_app.models import Supplier, StockIn, StockInDetail, Material

from first_app.models import StatusMaster, PurchaseOrderDetail, PurchaseOrder

LOW_STOCK_SENT = {}  # Lưu trạng thái gửi email theo material_id


class InventoryService:
#trừ tồn kho nguyên liệu khi khách order
    @staticmethod
    def reduce_inventory(order):
        order_details = OrderDetail.objects.filter(order=order)
        for detail in order_details:
            product = detail.product
            qty_product = detail.quantity
            materials = ProductMaterial.objects.filter(product=product)
            for pm in materials:
                material = pm.material
                required_amount = pm.quantity_required
                total_used = qty_product * required_amount
                inventory = Inventory.objects.filter(material=material).first()
                if not inventory:
                    print(f"[WARNING] Không có tồn kho cho {material.material_name}")
                    continue

                before_qty = inventory.quantity
                inventory.quantity = max(0, before_qty - total_used)
                inventory.save()

                print(f"[INVENTORY] {material.material_name}: {before_qty} -> {inventory.quantity}")

                InventoryService.check_and_alert(inventory)
#kiểm tra tồn kho cảnh báo sắp hết hàng
    @staticmethod
    def check_and_alert(inventory):
        material_id = inventory.material.material_id

        if inventory.quantity <= inventory.min_quantity:
            if not LOW_STOCK_SENT.get(material_id, False):
                InventoryService.send_low_stock_email(inventory)
                LOW_STOCK_SENT[material_id] = True
        else:
            if LOW_STOCK_SENT.get(material_id, False):
                LOW_STOCK_SENT[material_id] = False
                print(f"[RESET] {inventory.material.material_name}")
    @staticmethod
    def send_low_stock_email(inventory):

        subject = f"[Cảnh báo tồn kho] {inventory.material.material_name} sắp hết!"
        message = (
            f"Nguyên liệu: {inventory.material.material_name}\n"
            f"Số lượng còn lại: {inventory.quantity} {inventory.material.unit}\n"
            f"Ngưỡng cảnh báo: {inventory.min_quantity} {inventory.material.unit}\n"
            f"Vui lòng nhập thêm nguyên liệu."
        )
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
            )
            print("[EMAIL SENT]", inventory.material.material_name)
        except Exception as e:
            print("[EMAIL ERROR]", e)

    #phiếu nhập tồn kho
    @staticmethod
    def create_stockin(supplier_id, items, po_id=None):
        supplier = Supplier.objects.get(pk=supplier_id)
        stockin = StockIn.objects.create(
            supplier=supplier,
            po_id=po_id,
            created_at=timezone.now()
        )

        po = None
        if po_id:
            po = PurchaseOrder.objects.get(pk=po_id)

        all_received = True

        for item in items:
            material = Material.objects.get(pk=item["material_id"])
            quantity = float(item.get("quantity", 0))
            if quantity <= 0:
                continue

            # Kiểm tra nếu có PO
            if po:
                po_detail = PurchaseOrderDetail.objects.filter(po=po, material=material).first()
                if not po_detail:
                    raise ValueError(f"Nguyên liệu '{material.material_name}' không có trong PO {po.po_id}")
                if po.supplier_id != supplier.id:
                    raise ValueError(f"Nhà cung cấp '{supplier.user.username}' không đúng với PO {po.po_id}")
                if quantity > po_detail.quantity:
                    raise ValueError(
                        f"Số lượng nhập '{material.material_name}' vượt quá số lượng đã đặt ({po_detail.quantity})")

                # Nếu nhập ít hơn số lượng PO, đánh dấu nhận thiếu
                if quantity < po_detail.quantity:
                    all_received = False

            # Tạo chi tiết StockIn
            StockInDetail.objects.create(
                stockin=stockin,
                material=material,
                quantity=quantity,
                created_at=timezone.now()
            )

            # Cập nhật tồn kho
            inventory, _ = Inventory.objects.get_or_create(
                material=material,
                defaults={"quantity": 0}
            )
            inventory.quantity += quantity
            inventory.save()

        # Cập nhật trạng thái PO
        if po:
            if all_received:
                po.status = StatusMaster.objects.get(status_code=8)  # nhận đủ
            else:
                po.status = StatusMaster.objects.get(status_code=9)  # nhận thiếu
            po.save()

        return stockin
