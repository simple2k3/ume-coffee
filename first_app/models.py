from django.core.validators import RegexValidator
from django.db import models
import uuid
from django.contrib.auth.models import User
def generate_request_id():
    return str(uuid.uuid4())
def generate_order_id():
    return str(uuid.uuid4())
class StatusMaster(models.Model):
    status_code = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=100)
    update_by = models.CharField(max_length=100)
    update_time = models.DateTimeField()

    def __str__(self):
        return self.status_name

class Categories(models.Model):
    categories_id = models.CharField(max_length=50, primary_key=True)
    categories_name = models.CharField(max_length=100)
    imageUrl = models.URLField(max_length=500, blank=True, null=True)
    def __str__(self):
        return self.categories_name


class ProductMaster(models.Model):
    product_code = models.CharField(max_length=50, primary_key=True)
    product_name = models.CharField(max_length=255,validators=[RegexValidator( regex=r'[A-Za-zÀ-ỹ]',)])
    imageUrl = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    update_by = models.CharField(max_length=100)
    update_time = models.DateTimeField()
    category = models.ForeignKey(Categories,on_delete=models.CASCADE,related_name='products',null=True,blank=True)

    def __str__(self):
        return self.product_name

class TableMaster(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=100)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return self.table_name

class Order(models.Model):
    id=models.AutoField(primary_key=True)
    partnerCode = models.CharField(max_length=50)
    requestId = models.CharField(max_length=50, unique=True, default=generate_request_id)
    amount = models.BigIntegerField()
    orderId = models.CharField(max_length=200, unique=True, default=generate_order_id)
    orderInfo = models.CharField(max_length=255, blank=True)
    redirectUrl = models.URLField()
    requestType = models.CharField(max_length=50, default='captureWallet')
    extraData = models.TextField(blank=True)
    lang = models.CharField(max_length=2, default='vi')
    signature = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(StatusMaster,on_delete=models.SET_NULL,null=True,blank=True,related_name='orders')
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    customer = models.ForeignKey('Customer',on_delete=models.SET_NULL,null=True,blank=True,related_name='orders'

    )
    def __str__(self):
        return f"Order {self.orderId} - {self.status}"
    table = models.ForeignKey(TableMaster, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')



class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    totalPrice = models.FloatField(default=0)
    quantity = models.IntegerField(default=1)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OrderDetail {self.id} - {self.product.product_name}"


class Customer(models.Model):
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15,unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.customer_name} ({self.phone})"

class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    material_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)  # g, ml, kg, viên...

    def __str__(self):
        return self.material_name


class Inventory(models.Model):
    material = models.OneToOneField(Material,on_delete=models.CASCADE,primary_key=True,related_name='inventory' )
    quantity = models.FloatField(default=0)           # Số lượng còn lại
    min_quantity = models.FloatField(default=10)      # Ngưỡng cảnh báo
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material.material_name} - {self.quantity} {self.material.unit}"

class ProductMaterial(models.Model):
    product = models.ForeignKey( ProductMaster, on_delete=models.CASCADE,related_name='materials')
    material = models.ForeignKey(Material,on_delete=models.CASCADE,related_name='products')
    quantity_required = models.FloatField()  # số lượng material cho 1 sản phẩm
    class Meta:unique_together = ('product', 'material')

    def __str__(self):
        return f"{self.product.product_name} cần {self.quantity_required} {self.material.unit} {self.material.material_name}"

# chưa update
class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} profile"

class PurchaseOrder(models.Model):
    po_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders',null=True,blank=True )
    created_at = models.DateTimeField(auto_now_add=True)
    expected_date = models.DateTimeField(blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    status = models.ForeignKey(StatusMaster, on_delete=models.CASCADE, related_name='purchase_orders')

    def __str__(self):
        if self.supplier and self.supplier.user:
            return f"PO {self.po_id} - {self.supplier.user.username}"
        return f"PO {self.po_id} - Chưa có nhà cung cấp"

class PurchaseOrderDetail(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='details')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.FloatField()
    def __str__(self):
        return f"PO {self.po.po_id} - {self.material.material_name} ({self.quantity})"

class StockIn(models.Model):
    stockin_id = models.AutoField(primary_key=True)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='stockins')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"StockIn {self.stockin_id}"

class StockInDetail(models.Model):
    stockin = models.ForeignKey(StockIn, on_delete=models.CASCADE, related_name='details')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.material.material_name} nhập {self.quantity}"