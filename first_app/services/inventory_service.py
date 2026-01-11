# first_app/services/inventory_service.py
from django.utils import timezone

from django.core.mail import send_mail
from django.conf import settings
from first_app.models import Inventory, ProductMaterial, OrderDetail

from first_app.models import Supplier, StockIn, StockInDetail, Material

from first_app.models import StatusMaster, PurchaseOrderDetail, PurchaseOrder

LOW_STOCK_SENT = {}  #để đánh dấu mức tồn kho đạt ngưỡng thì sẽ gửi cảnh báo
class InventoryService:
#trừ tồn kho nguyên liệu khi khách order
    @staticmethod
    def reduce_inventory(order):
        # Chỉ chạy nếu trạng thái là 2
        if not order.status or order.status.status_code != 2:
            print(f"Đơn hàng {order.orderId} chưa ở trạng thái 2. Không trừ kho.")
            return
        #Thực hiện trừ tồn kho
        order_details = OrderDetail.objects.filter(order=order)
        for detail in order_details:
            product = detail.product
            qty_product = detail.quantity
            materials = ProductMaterial.objects.filter(product=product)
            for pm in materials:
                material = pm.material
                required_amount = pm.quantity_required
                total_used = qty_product * required_amount#tổng nguyên liệu tiêu hao

                inventory = Inventory.objects.filter(material=material).first()
                if not inventory:
                    continue

                before_qty = inventory.quantity #lấy tônf kho ban đầu
                inventory.quantity = max(0, before_qty - total_used)#rồi trừ cho tổng nguyên liệu tiêu hao trong đơn hàng ko cho âm
                inventory.save()

                # print(f"[INVENTORY] {material.material_name}: {before_qty} -> {inventory.quantity}")
                InventoryService.check_and_alert(inventory)
#kiểm tra tồn kho cảnh báo sắp hết hàng
    @staticmethod
    def check_and_alert(inventory):
        material_id = inventory.material.material_id
        if inventory.quantity <= inventory.min_quantity:# kiểm tra nếu đạt ngưỡng
            if not LOW_STOCK_SENT.get(material_id, False):
                InventoryService.send_low_stock_email(inventory)#gửi email
                LOW_STOCK_SENT[material_id] = True #đánh dấu đã gửi
        else:
            if LOW_STOCK_SENT.get(material_id, False):#Nếu trước đó từng gửi cảnh báo
                LOW_STOCK_SENT[material_id] = False#Đặt lại trạng thái
                # print(f"[RESET] {inventory.material.material_name}")
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
    def create_stockin(items, po_id=None):
        po = None
        if po_id:
            try:
                po = PurchaseOrder.objects.get(pk=po_id)
            except PurchaseOrder.DoesNotExist:
                raise ValueError(f"Không tìm thấy đơn hàng PO với ID: {po_id}")

        stockin = StockIn.objects.create(
            po=po,
            created_at=timezone.now()
        )
        all_received = True
        for item in items:
            material = Material.objects.get(pk=item["material_id"])
            quantity = float(item.get("quantity", 0))
            if quantity <= 0: continue
            if po:
                po_detail = PurchaseOrderDetail.objects.filter(po=po, material=material).first()
                if po_detail:
                    if quantity > po_detail.quantity:
                        raise ValueError(f"Số lượng nhập '{material.material_name}' vượt quá PO")
                    if quantity < po_detail.quantity:
                        all_received = False
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
            try:
                status_code = 8 if all_received else 9
                po.status = StatusMaster.objects.get(status_code=status_code)
                po.save()
            except StatusMaster.DoesNotExist:
                pass
        return stockin


# def create_stockin(items, po_id):
#     if not po_id:
#         raise ValueError("Bắt buộc phải chọn phiếu đặt hàng (PO) để nhập kho")
#
#     try:
#         po = PurchaseOrder.objects.get(pk=po_id)
#     except PurchaseOrder.DoesNotExist:
#         raise ValueError(f"Không tìm thấy đơn hàng PO với ID: {po_id}")
#
#     stockin = StockIn.objects.create(
#         po=po,
#         created_at=timezone.now()
#     )
#
#     all_received = True
#
#     for item in items:
#         material = Material.objects.get(pk=item["material_id"])
#         quantity = float(item.get("quantity", 0))
#         if quantity <= 0:
#             continue
#
#         po_detail = PurchaseOrderDetail.objects.filter(po=po, material=material).first()
#         if not po_detail:
#             raise ValueError(f"Nguyên liệu '{material.material_name}' không có trong PO")
#
#         if quantity > po_detail.quantity:
#             raise ValueError(f"Số lượng nhập '{material.material_name}' vượt quá PO")
#
#         if quantity < po_detail.quantity:
#             all_received = False
#
#         StockInDetail.objects.create(
#             stockin=stockin,
#             material=material,
#             quantity=quantity,
#             created_at=timezone.now()
#         )
#
#         inventory, _ = Inventory.objects.get_or_create(
#             material=material,
#             defaults={"quantity": 0}
#         )
#         inventory.quantity += quantity
#         inventory.save()
#
#     status_code = 8 if all_received else 9
#     po.status = StatusMaster.objects.get(status_code=status_code)
#     po.save()
#
#     return stockin