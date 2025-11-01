from django.db import models
import uuid
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
    product_name = models.CharField(max_length=255)
    imageUrl = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    update_by = models.CharField(max_length=100)
    update_time = models.DateTimeField()
    category = models.ForeignKey(Categories,on_delete=models.CASCADE,related_name='products',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.product_name


class TableMaster(models.Model):
    table_name = models.CharField(max_length=100)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return self.table_name


class Order(models.Model):
    id=models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=100, default=generate_order_id)
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
    create_at = models.DateTimeField()

    def __str__(self):
        return f"OrderDetail {self.id} - {self.product.product_name}"


class Customer(models.Model):
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15,unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.customer_name} ({self.phone})"
