from rest_framework import serializers

from accounts.models import ProviderProfile
from .models import Category, Commune


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']
        read_only_fields = fields


class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = ['id', 'name', 'slug']
        read_only_fields = fields


class ProviderListSerializer(serializers.ModelSerializer):
    """Prestador en listado de búsqueda (sin datos privados)."""

    phone = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField(read_only=True, allow_null=True)
    rating_count = serializers.IntegerField(read_only=True)

    def get_latitude(self, obj):
        return obj.latitude if obj.map_visible else None

    def get_longitude(self, obj):
        return obj.longitude if obj.map_visible else None

    def get_distance_km(self, obj):
        value = getattr(obj, 'distance_km', None)
        return round(value, 2) if value is not None else None

    def get_phone(self, obj):
        return ''

    user_id = serializers.IntegerField(source='user.id', read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    communes = CommuneSerializer(many=True, read_only=True)

    class Meta:
        model = ProviderProfile
        fields = [
            'id', 'user_id', 'display_name', 'description',
            'years_experience', 'phone', 'categories', 'communes',
            'is_active', 'is_verified',
            'latitude', 'longitude', 'map_visible', 'distance_km', 'avatar', 'avg_rating', 'rating_count',
        ]
        read_only_fields = fields


class ProviderDetailSerializer(ProviderListSerializer):
    """Detalle completo del prestador (público)."""
    pass
