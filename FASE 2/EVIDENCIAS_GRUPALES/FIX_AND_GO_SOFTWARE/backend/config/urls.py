from django.contrib import admin
from django.urls import include, path
from core.views import health
from catalog.map_view import map_document

urlpatterns = [
    path('map/', map_document, name='map-document'),
    path('admin/', admin.site.urls),
    path('api/v1/health/', health, name='health'),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/', include('catalog.urls')),
    path('api/v1/', include('services.urls')),
    path('api/v1/', include('billing.urls')),
]
