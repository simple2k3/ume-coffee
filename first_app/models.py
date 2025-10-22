from django.db import models
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

    def __str__(self):
        return self.categories_name


class ProductMaster(models.Model):
    product_code = models.CharField(max_length=50, primary_key=True)
    product_name = models.CharField(max_length=255)
    image = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    base_price = models.FloatField()
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
    status = models.ForeignKey('StatusMaster', on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return self.table_name


class Orders(models.Model):
    table = models.ForeignKey(TableMaster, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusMaster, on_delete=models.CASCADE)
    total_invoice = models.FloatField()
    create_at = models.DateTimeField()

    def __str__(self):
        return f"Order {self.id}"


class OrderDetail(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    quantity_product = models.IntegerField()
    create_at = models.DateTimeField()

    def __str__(self):
        return f"OrderDetail {self.id} - {self.product.product_name}"
