
from django.contrib import admin
from django.urls import path
from first_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),
    path('portfolio.html', views.portfolio, name='portfolio'),
    path('contact/', views.contact, name='contact'),
    path('admin/', admin.site.urls),
    path('print-qr/<int:table_id>/', views.print_qr, name='print_qr'),
    path('table/<int:table_id>/', views.table_order, name='table_order'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_DIR)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)