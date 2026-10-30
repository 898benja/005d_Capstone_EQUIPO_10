"""Admin de la app services (BE-13).

Búsquedas, filtros y columnas útiles para solicitudes, cotizaciones y valoraciones.
"""

from django.contrib import admin

from .models import Quote, Rating, ServiceRequest


class BusinessReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


@admin.register(ServiceRequest)
class ServiceRequestAdmin(BusinessReadOnlyAdmin):
    """Administración de solicitudes de servicio.

    BE-13: búsqueda por cliente/prestador, filtros por estado/categoría/comuna,
    fechas como readonly, enlace rápido a cotización.
    """

    list_display = [
        'id', 'status', 'client', 'provider', 'category',
        'commune', 'created_at', 'updated_at',
    ]
    list_filter = ['status', 'category', 'commune', 'created_at']
    search_fields = [
        'client__email', 'client__first_name', 'client__last_name',
        'provider__email', 'provider__first_name',
        'description',
    ]
    raw_id_fields = ['client', 'provider']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'

    # BE-13: bloquear edición de estado desde admin
    # (las transiciones deben pasar por la API)


@admin.register(Quote)
class QuoteAdmin(BusinessReadOnlyAdmin):
    """Administración de cotizaciones.

    BE-13: vista con precio formateado, filtros por estado.
    """

    list_display = [
        'id', 'service_request', 'provider', 'formatted_price',
        'status', 'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'service_request__id', 'provider__email',
        'description',
    ]
    raw_id_fields = ['service_request', 'provider']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25

    @admin.display(description='Precio (CLP)')
    def formatted_price(self, obj):
        return f'${obj.price:,}'


@admin.register(Rating)
class RatingAdmin(BusinessReadOnlyAdmin):
    """Administración de valoraciones (P2 — BE-18)."""

    list_display = ['id', 'service_request', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['service_request']
    list_per_page = 25
