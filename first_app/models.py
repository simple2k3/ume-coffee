# from django.db import models
# import qrcode
# from io import BytesIO
# from django.core.files import File
# import urllib.parse
#
# class Table(models.Model):
#     name = models.CharField(max_length=100)
#     qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
#
#     def save(self, *args, **kwargs):
#         creating = self.pk is None
#         super().save(*args, **kwargs)
#
#         if creating:
#             base_url = "https://67e720cfd4d6.ngrok-free.app"
#             encoded_name = urllib.parse.quote(self.name)
#             qr_data = f"{base_url}/index.html?tableId={self.id}&tableName={encoded_name}"
#
#             qr_img = qrcode.make(qr_data)
#             blob = BytesIO()
#             qr_img.save(blob, 'PNG')
#             self.qr_code.save(f"table_{self.id}.png", File(blob), save=False)
#
#             super().save(update_fields=['qr_code'])
#
#     def __str__(self):
#         return self.name


from django.db import models

# Bảng StatusMaster
class StatusMaster(models.Model):
    status_code = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=100)
    update_by = models.CharField(max_length=100)
    update_time = models.DateTimeField()

    def __str__(self):
        return self.status_name


# Bảng Categories
class Categories(models.Model):
    categories_id = models.CharField(max_length=50, primary_key=True)
    categories_name = models.CharField(max_length=100)

    def __str__(self):
        return self.categories_name


# Bảng ProductMaster
class ProductMaster(models.Model):
    product_code = models.CharField(max_length=50, primary_key=True)
    product_name = models.CharField(max_length=255)
    image = models.URLField(max_length=500, blank=True, null=True)
    base_price = models.FloatField()
    is_active = models.BooleanField()
    update_by = models.CharField(max_length=100)
    update_time = models.DateTimeField()


    def __str__(self):
        return self.product_name


# Bảng Categories_Product
class CategoriesProduct(models.Model):
    categories = models.ForeignKey(Categories, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    create_at = models.DateTimeField()

    class Meta:
        unique_together = (('categories', 'product'),)

    def __str__(self):
        return f"{self.categories} - {self.product}"


# Bảng TableMaster
class TableMaster(models.Model):
    table_name = models.CharField(max_length=100)
    status = models.ForeignKey(StatusMaster, on_delete=models.CASCADE)

    def __str__(self):
        return self.table_name


# Bảng Orders
class Orders(models.Model):
    table = models.ForeignKey(TableMaster, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusMaster, on_delete=models.CASCADE)
    customer_id = models.IntegerField(null=True, blank=True)  # Nếu có bảng Customer thì dùng FK
    total_invoice = models.FloatField()
    create_at = models.DateTimeField()

    def __str__(self):
        return f"Order {self.id}"


# Bảng OrderDetail
class OrderDetail(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    quantity_product = models.IntegerField()
    create_at = models.DateTimeField()

    def __str__(self):
        return f"OrderDetail {self.id} - {self.product}"
