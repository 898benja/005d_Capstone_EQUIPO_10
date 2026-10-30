from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Identidad extensible con rol de negocio.

    Restricciones:
    - El correo electrónico es único sin distinguir mayúsculas (BD-02).
    - El rol es inmutable después de la creación (validado en serializers).
    - Un usuario con rol PROVIDER debe tener un ProviderProfile asociado
      (la creación automática se maneja en el serializer de registro).
    """

    # Datos privados reutilizables: nunca se incluyen en el catálogo público.
    phone = models.CharField(max_length=20, blank=True)
    default_address = models.CharField(max_length=300, blank=True)
    default_commune = models.ForeignKey(
        'catalog.Commune', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='resident_users',
    )

    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Cliente'
        PROVIDER = 'PROVIDER', 'Prestador'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name='rol',
    )
    email = models.EmailField('correo electrónico', unique=True)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        # BD-02: índice para búsqueda rápida por rol
        indexes = [
            models.Index(fields=['role'], name='idx_user_role'),
            models.Index(fields=['email'], name='idx_user_email'),
        ]

    def save(self, *args, **kwargs):
        """Normaliza email a minúsculas antes de guardar (BD-02)."""
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def clean(self):
        """Validación a nivel de modelo: el rol debe ser válido."""
        super().clean()
        if self.role not in dict(self.Role.choices):
            raise ValidationError({'role': 'Rol no válido.'})

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'


class ProviderProfile(models.Model):
    """Perfil público del prestador de servicios.

    Restricciones:
    - Solo usuarios con rol PROVIDER pueden tener perfil (limit_choices_to).
    - Un usuario solo puede tener un perfil (OneToOneField).
    - El perfil debe tener un nombre visible no vacío.
    """

    # Punto de atención publicado voluntariamente; nunca GPS ni domicilio privado.
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    map_visible = models.BooleanField(default=False)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='provider_profile',
        limit_choices_to={'role': User.Role.PROVIDER},
    )
    display_name = models.CharField('nombre visible', max_length=120)
    avatar = models.TextField(blank=True, editable=False)
    description = models.TextField('descripción', blank=True)
    years_experience = models.PositiveIntegerField(
        'años de experiencia', null=True, blank=True,
    )
    phone = models.CharField(
        'teléfono demostrativo', max_length=20, blank=True,
        help_text='Número ficticio para la demostración.',
    )
    categories = models.ManyToManyField(
        'catalog.Category',
        related_name='providers',
        verbose_name='categorías',
        blank=True,
    )
    communes = models.ManyToManyField(
        'catalog.Commune',
        related_name='providers',
        verbose_name='comunas',
        blank=True,
    )
    is_active = models.BooleanField('activo', default=True)
    is_verified = models.BooleanField(
        'verificación simulada', default=False,
        help_text='Dato demostrativo. FIX&GO no verificó realmente credenciales profesionales.',
    )

    class Meta:
        verbose_name = 'perfil de prestador'
        verbose_name_plural = 'perfiles de prestadores'
        ordering = ['display_name']
        # BD-06: índice para búsqueda de perfiles activos
        indexes = [
            models.Index(fields=['is_active'], name='idx_provider_active'),
            models.Index(fields=['map_visible', 'latitude', 'longitude'], name='idx_provider_map'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(latitude__isnull=True, longitude__isnull=True)
                           | models.Q(latitude__isnull=False, longitude__isnull=False,
                                      latitude__gte=-33.85, latitude__lte=-33.1,
                                      longitude__gte=-71.1, longitude__lte=-70.35)),
                name='provider_point_santiago',
            ),
            models.CheckConstraint(
                condition=models.Q(map_visible=False) | models.Q(latitude__isnull=False, longitude__isnull=False),
                name='provider_map_requires_point',
            ),
        ]

    def clean(self):
        """Validación: solo usuarios PROVIDER pueden tener perfil."""
        if self.user_id and self.user.role != User.Role.PROVIDER:
            raise ValidationError(
                'Solo los usuarios con rol PROVIDER pueden tener perfil de prestador.'
            )

    def __str__(self):
        return self.display_name
