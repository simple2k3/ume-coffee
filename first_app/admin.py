from django.contrib import admin
from .models import Categories
from .models import TableMaster
from .models import ProductMaster
admin.site.register(Categories)
admin.site.register(TableMaster)
admin.site.register(ProductMaster)