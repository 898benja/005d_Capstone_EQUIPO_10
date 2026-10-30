"""Serializers de la app accounts.

Cubre BE-02 (registro e inicio de sesión), BE-03 (token), BE-05 (perfil prestador).
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import ProviderProfile, User
from .profile import PersonalProfileSerializer
from catalog.models import Commune


# ---------------------------------------------------------------------------
# Autenticación (BE-02, BE-03)
# ---------------------------------------------------------------------------

class RegisterSerializer(serializers.Serializer):
    """Registro de nuevo usuario con rol.

    Validaciones:
    - Correo único sin distinguir mayúsculas.
    - Contraseña validada contra las reglas de Django.
    - display_name obligatorio si el rol es PROVIDER.
    """

    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=User.Role.choices)
    # Datos reutilizables opcionales para mantener compatibilidad con cuentas existentes.
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    default_address = serializers.CharField(max_length=300, required=False, allow_blank=True)
    default_commune = serializers.PrimaryKeyRelatedField(queryset=Commune.objects.all(), required=False, allow_null=True)

    def validate_phone(self, value):
        return PersonalProfileSerializer().validate_phone(value)

    # Solo para prestadores
    display_name = serializers.CharField(max_length=120, required=False)

    def validate_email(self, value):
        """BD-02: email único sin distinguir mayúsculas."""
        normalized = value.lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError(
                'Ya existe una cuenta con este correo electrónico.'
            )
        return normalized

    def validate_password(self, value):
        """BE-02: validar contraseña contra las reglas de Django."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Validación cruzada: display_name requerido para prestadores."""
        if attrs['role'] == User.Role.PROVIDER and not attrs.get('display_name'):
            raise serializers.ValidationError(
                {'display_name': 'El nombre visible es obligatorio para prestadores.'}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Crear usuario, perfil de prestador (si aplica) y token."""
        display_name = validated_data.pop('display_name', '')
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        email = validated_data['email']

        # Usuario, perfil y token se confirman juntos. Si falla cualquiera,
        # el correo queda libre para reintentar el registro sin cuentas huérfanas.
        user = User(
            username=email,
            email=email,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=role,
            phone=validated_data.get('phone', ''),
            default_address=validated_data.get('default_address', ''),
            default_commune=validated_data.get('default_commune'),
        )
        user.set_password(password)
        user.save()

        # Crear perfil de prestador automáticamente (BD-02)
        if role == User.Role.PROVIDER:
            ProviderProfile.objects.create(user=user, display_name=display_name)

        token = Token.objects.create(user=user)
        return user, token


class LoginSerializer(serializers.Serializer):
    """Autenticación por correo y contraseña.

    BE-02: cubrir login correcto, incorrecto y cuenta inactiva.
    """

    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email'].lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'detail': 'Credenciales inválidas.'}
            )

        user = authenticate(username=user.username, password=attrs['password'])
        if user is None:
            raise serializers.ValidationError(
                {'detail': 'Credenciales inválidas.'}
            )
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Datos del usuario autenticado — sin datos sensibles."""

    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'role_display', 'phone', 'default_address', 'default_commune']
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Perfil de prestador (BE-05)
# ---------------------------------------------------------------------------

class ProviderProfileReadSerializer(serializers.ModelSerializer):
    """Perfil público de prestador (lectura).

    BE-06: no expone datos privados innecesarios.
    """

    user_id = serializers.IntegerField(source='user.id', read_only=True)
    categories = serializers.SerializerMethodField()
    communes = serializers.SerializerMethodField()

    class Meta:
        model = ProviderProfile
        fields = [
            'id', 'user_id', 'display_name', 'description',
            'years_experience', 'phone', 'categories', 'communes',
            'is_active', 'is_verified',
            'latitude', 'longitude', 'map_visible', 'avatar',
        ]
        read_only_fields = fields

    def get_categories(self, obj):
        return list(obj.categories.values('id', 'name', 'slug'))

    def get_communes(self, obj):
        return list(obj.communes.values('id', 'name', 'slug'))


class _LazyCategoryField(serializers.PrimaryKeyRelatedField):
    """Referencia lazy a categorías para evitar imports circulares."""

    def get_queryset(self):
        from catalog.models import Category
        return Category.objects.all()


class _LazyCommuneField(serializers.PrimaryKeyRelatedField):
    """Referencia lazy a comunas para evitar imports circulares."""

    def get_queryset(self):
        from catalog.models import Commune
        return Commune.objects.all()


class ProviderProfileWriteSerializer(serializers.ModelSerializer):
    """Perfil de prestador (escritura — solo propietario).

    BE-05: validar nombre visible, experiencia, categorías y comunas.
    """

    categories = _LazyCategoryField(many=True, required=False)
    communes = _LazyCommuneField(many=True, required=False)

    class Meta:
        model = ProviderProfile
        fields = [
            'display_name', 'description', 'years_experience',
            'phone', 'categories', 'communes', 'is_active',
            'latitude', 'longitude', 'map_visible',
        ]

    def validate(self, attrs):
        from catalog.geo import validate_point
        lat = attrs.get('latitude', getattr(self.instance, 'latitude', None))
        lon = attrs.get('longitude', getattr(self.instance, 'longitude', None))
        visible = attrs.get('map_visible', getattr(self.instance, 'map_visible', False))
        if (lat is None) != (lon is None):
            raise serializers.ValidationError('Indica ambas coordenadas o elimina ambas.')
        if lat is not None:
            validate_point(lat, lon)
        if visible and lat is None:
            raise serializers.ValidationError('Selecciona un punto antes de publicar tu zona.')
        return attrs

    def validate_display_name(self, value):
        """BE-05: el nombre visible no puede estar vacío."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                'El nombre visible no puede estar vacío.'
            )
        return value.strip()

    def validate_years_experience(self, value):
        """BE-05: experiencia razonable."""
        if value is not None and value > 70:
            raise serializers.ValidationError(
                'Los años de experiencia no parecen razonables.'
            )
        return value

    def validate_phone(self, value):
        """BE-05: formato básico de teléfono demo."""
        if value and len(value.strip()) < 8:
            raise serializers.ValidationError(
                'El teléfono debe tener al menos 8 caracteres.'
            )
        return value.strip() if value else value
