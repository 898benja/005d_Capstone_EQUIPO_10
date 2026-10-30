"""Serializers de la app services.

Cubre BE-07 (creación de solicitudes), BE-08 (listado/detalle), BE-09 (cotizaciones),
BE-17 (cierre), BE-18 (valoración).
"""

from rest_framework import serializers

from accounts.models import ProviderProfile, User
from catalog.models import Category, Commune
from .models import Quote, Rating, ServiceRequest


# ---------------------------------------------------------------------------
# Solicitudes
# ---------------------------------------------------------------------------

class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    """Crear una solicitud (solo clientes).

    BE-07: Validar que el prestador esté activo, ofrezca la categoría
    solicitada y atienda la comuna seleccionada.
    """

    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.PROVIDER, is_active=True),
        source='provider',
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category',
    )
    commune_id = serializers.PrimaryKeyRelatedField(
        queryset=Commune.objects.all(), source='commune',
    )

    class Meta:
        model = ServiceRequest
        fields = [
            'provider_id', 'category_id', 'commune_id',
            'address', 'description', 'preferred_date', 'preferred_time',
            'latitude', 'longitude',
        ]

    def validate_description(self, value):
        """La descripción debe tener al menos 10 caracteres significativos."""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                'La descripción debe tener al menos 10 caracteres.'
            )
        return value

    def validate(self, attrs):
        """BE-07: validaciones cruzadas de negocio."""
        provider = attrs['provider']
        from catalog.geo import validate_point
        lat, lon = attrs.get('latitude'), attrs.get('longitude')
        if (lat is None) != (lon is None):
            raise serializers.ValidationError('Indica ambas coordenadas.')
        if lat is not None:
            validate_point(lat, lon)
        category = attrs['category']
        commune = attrs['commune']

        # Verificar que el prestador tenga perfil activo
        try:
            profile = provider.provider_profile
        except ProviderProfile.DoesNotExist:
            raise serializers.ValidationError(
                {'provider_id': 'El prestador no tiene un perfil configurado.'}
            )

        if not profile.is_active:
            raise serializers.ValidationError(
                {'provider_id': 'El prestador no está activo actualmente.'}
            )

        # Verificar que el prestador ofrece la categoría solicitada
        if not profile.categories.filter(pk=category.pk).exists():
            raise serializers.ValidationError(
                {'category_id': f'El prestador no ofrece la categoría "{category.name}".'}
            )

        # Verificar que el prestador atiende la comuna solicitada
        if not profile.communes.filter(pk=commune.pk).exists():
            raise serializers.ValidationError(
                {'commune_id': f'El prestador no atiende la comuna "{commune.name}".'}
            )

        # BD-03: el cliente y el prestador no pueden ser el mismo usuario
        request = self.context.get('request')
        if request and request.user.id == provider.id:
            raise serializers.ValidationError(
                'No puedes crear una solicitud a ti mismo.'
            )

        return attrs

    def create(self, validated_data):
        """Asignar cliente y estado inicial."""
        validated_data['client'] = self.context['request'].user
        validated_data['status'] = ServiceRequest.Status.PENDING
        return super().create(validated_data)


class QuoteReadSerializer(serializers.ModelSerializer):
    """Cotización (lectura).

    BE-09: incluye datos suficientes para que el cliente decida.
    """

    provider_name = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = [
            'id', 'provider', 'provider_name', 'description', 'price',
            'proposed_date', 'estimated_duration', 'notes',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_provider_name(self, obj):
        """Nombre visible del prestador."""
        profile = getattr(obj.provider, 'provider_profile', None)
        return profile.display_name if profile else obj.provider.get_full_name()


class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Solicitud en listado — sin dirección privada.

    BE-08: filtrar por rol, incluir historial mínimo, ocultar dirección.
    """

    category_name = serializers.CharField(source='category.name', read_only=True)
    commune_name = serializers.CharField(source='commune.name', read_only=True)
    client_name = serializers.SerializerMethodField()
    provider_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    has_active_quote = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'client', 'provider', 'client_name', 'provider_name',
            'category', 'category_name', 'commune', 'commune_name',
            'description', 'preferred_date', 'preferred_time',
            'status', 'status_display', 'has_active_quote',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_client_name(self, obj):
        return obj.client.get_full_name() or 'Cliente'

    def get_provider_name(self, obj):
        profile = getattr(obj.provider, 'provider_profile', None)
        return profile.display_name if profile else obj.provider.get_full_name()

    def get_has_active_quote(self, obj):
        """Indica si la solicitud tiene una cotización activa."""
        return obj.quotes.filter(
            status__in=[Quote.Status.SUBMITTED, Quote.Status.ACCEPTED]
        ).exists()


class ServiceRequestDetailSerializer(ServiceRequestListSerializer):
    """Detalle de solicitud — incluye dirección solo para partes autorizadas.

    BE-08: dirección visible solo para cliente, prestador asignado o staff.
    """

    address = serializers.SerializerMethodField()
    quote = serializers.SerializerMethodField()

    class Meta(ServiceRequestListSerializer.Meta):
        fields = ServiceRequestListSerializer.Meta.fields + ['address', 'quote', 'latitude', 'longitude']

    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    def get_latitude(self, obj):
        return obj.latitude if self.get_address(obj) is not None else None

    def get_longitude(self, obj):
        return obj.longitude if self.get_address(obj) is not None else None

    def get_address(self, obj):
        """BE-08: ocultar dirección en respuestas a terceros."""
        request = self.context.get('request')
        if not request:
            return None
        user = request.user
        if user and (user.id == obj.client_id or user.id == obj.provider_id or user.is_staff):
            return obj.address
        return None

    def get_quote(self, obj):
        """Incluir la cotización activa o aceptada en el detalle."""
        quote = obj.quotes.filter(
            status__in=[Quote.Status.SUBMITTED, Quote.Status.ACCEPTED]
        ).first()
        if quote:
            return QuoteReadSerializer(quote).data
        return None


# ---------------------------------------------------------------------------
# Cotizaciones (BE-09)
# ---------------------------------------------------------------------------

class QuoteCreateSerializer(serializers.ModelSerializer):
    """Crear cotización (solo prestador asignado).

    BE-09: monto positivo entero, una sola cotización activa.
    """

    class Meta:
        model = Quote
        fields = [
            'description', 'price', 'proposed_date',
            'estimated_duration', 'notes',
        ]

    def validate_price(self, value):
        """BE-09: monto positivo entero."""
        if value is None or value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor que cero.')
        return value

    def validate_description(self, value):
        """La descripción del trabajo es obligatoria."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                'La descripción del trabajo incluido es obligatoria.'
            )
        return value


# ---------------------------------------------------------------------------
# Valoraciones (P2 — BE-18)
# ---------------------------------------------------------------------------

class RatingCreateSerializer(serializers.ModelSerializer):
    """Crear valoración — solo cliente del servicio completado."""

    class Meta:
        model = Rating
        fields = ['score', 'comment']

    def validate_score(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError(
                'El puntaje debe estar entre 1 y 5.'
            )
        return value


class RatingReadSerializer(serializers.ModelSerializer):
    """Lectura de valoración."""

    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ['id', 'score', 'comment', 'client_name', 'created_at']
        read_only_fields = fields

    def get_client_name(self, obj):
        return (obj.service_request.client.get_full_name()
                or 'Cliente')
