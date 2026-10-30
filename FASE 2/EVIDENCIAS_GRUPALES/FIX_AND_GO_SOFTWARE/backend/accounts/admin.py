"""Admin de la app accounts (BE-13).

Búsquedas, filtros y columnas útiles para usuarios y perfiles.
Bloqueo de ediciones peligrosas (rol y contraseña no editables directamente).
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ProviderProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administración de usuarios FIX&GO.

    BE-13: búsqueda por email/nombre, filtros por rol/estado,
    columna de rol visible en el listado.
    """

    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_active', 'date_joined',
    ]
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    list_per_page = 25

    fieldsets = BaseUserAdmin.fieldsets + (
        ('FIX&GO', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('FIX&GO', {'fields': ('email', 'role')}),
    )

    # BE-13: bloquear edición de rol desde admin (solo visible)
    readonly_fields = ['date_joined', 'last_login']

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + (['role'] if obj else [])


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    """Administración de perfiles de prestadores.

    BE-13: búsqueda, filtros, vista de categorías y comunas.
    """

    list_display = [
        'display_name', 'user', 'is_active', 'is_verified',
        'years_experience', 'phone', 'get_categories', 'get_communes',
    ]
    list_filter = ['is_active', 'is_verified', 'categories', 'communes']
    search_fields = ['display_name', 'user__email', 'user__first_name', 'user__last_name']
    filter_horizontal = ['categories', 'communes']
    raw_id_fields = ['user']
    list_per_page = 25

    @admin.display(description='Categorías')
    def get_categories(self, obj):
        return ', '.join(c.name for c in obj.categories.all())

    @admin.display(description='Comunas')
    def get_communes(self, obj):
        return ', '.join(c.name for c in obj.communes.all())


# Personalización del sitio
admin.site.site_header = 'FIX&GO · Administración'
admin.site.site_title = 'FIX&GO Admin'
admin.site.index_title = 'Panel de administración'
