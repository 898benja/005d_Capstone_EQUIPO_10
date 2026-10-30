"""Admin de la app catalog (BE-13).

Búsquedas y filtros para categorías y comunas.
"""

from django.contrib import admin

from .models import Category, Commune


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'description']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
