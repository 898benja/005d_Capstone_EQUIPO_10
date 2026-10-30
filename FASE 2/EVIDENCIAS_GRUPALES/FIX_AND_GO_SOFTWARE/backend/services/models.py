from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ServiceRequest(models.Model):
    """Solicitud de servicio técnico de un cliente a un prestador.

    Restricciones (BD-03):
    - El cliente y el prestador no pueden ser el mismo usuario.
    - El prestador debe estar activo y ofrecer la categoría y comuna solicitadas (BE-07).
    - Los estados siguen la máquina: PENDING→QUOTED→ACCEPTED/REJECTED/CANCELLED.
    - CANCELLED solo es válido desde PENDING o QUOTED (no desde ACCEPTED).
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        QUOTED = 'QUOTED', 'Cotizada'
        ACCEPTED = 'ACCEPTED', 'Aceptada'
        REJECTED = 'REJECTED', 'Rechazada'
        CANCELLED = 'CANCELLED', 'Cancelada'
        # P2 — BE-17: estados futuros para cierre de servicio
        IN_PROGRESS = 'IN_PROGRESS', 'En progreso'
        COMPLETED = 'COMPLETED', 'Completada'

    # -----------------------------------------------------------------------
    # Transiciones de estado válidas (máquina de estados)
    # -----------------------------------------------------------------------
    VALID_TRANSITIONS = {
        Status.PENDING: [Status.QUOTED, Status.CANCELLED],
        Status.QUOTED: [Status.ACCEPTED, Status.REJECTED, Status.CANCELLED, Status.PENDING],
        Status.ACCEPTED: [Status.IN_PROGRESS],     # P2: iniciar servicio
        Status.REJECTED: [],                         # estado terminal
        Status.CANCELLED: [],                        # estado terminal
        Status.IN_PROGRESS: [Status.COMPLETED],      # P2: completar servicio
        Status.COMPLETED: [],                         # estado terminal
    }

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_requests',
        limit_choices_to={'role': 'CLIENT'},
        verbose_name='cliente',
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provider_requests',
        limit_choices_to={'role': 'PROVIDER'},
        verbose_name='prestador',
    )
    category = models.ForeignKey(
        'catalog.Category',
        on_delete=models.PROTECT,
        verbose_name='categoría',
    )
    commune = models.ForeignKey(
        'catalog.Commune',
        on_delete=models.PROTECT,
        verbose_name='comuna',
    )
    address = models.TextField(
        'dirección o referencia', blank=True,
        help_text='Dato privado: solo visible para el cliente, el prestador asignado y administradores.',
    )
    # Ubicación de la solicitud: solo se entrega a las partes autorizadas.
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.TextField('descripción del problema')
    preferred_date = models.DateField('fecha preferida', null=True, blank=True)
    preferred_time = models.CharField(
        'horario preferido', max_length=30, blank=True,
        help_text='Ej: mañana, tarde, noche.',
    )
    status = models.CharField(
        'estado', max_length=12,
        choices=Status.choices, default=Status.PENDING,
    )
    created_at = models.DateTimeField('creado', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado', auto_now=True)

    class Meta:
        verbose_name = 'solicitud de servicio'
        verbose_name_plural = 'solicitudes de servicio'
        ordering = ['-created_at']
        # BD-06: índices para consultas principales
        indexes = [
            models.Index(fields=['status'], name='idx_request_status'),
            models.Index(fields=['client', 'status'], name='idx_request_client_status'),
            models.Index(fields=['provider', 'status'], name='idx_request_prov_status'),
            models.Index(fields=['-created_at'], name='idx_request_created'),
        ]

    def clean(self):
        """BD-03: validaciones de integridad de la solicitud."""
        # El cliente y el prestador no pueden ser el mismo usuario
        if self.client_id and self.provider_id and self.client_id == self.provider_id:
            raise ValidationError(
                'El cliente y el prestador no pueden ser el mismo usuario.'
            )

    def can_transition_to(self, new_status):
        """Verifica si la transición de estado es válida."""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status):
        """Realiza la transición de estado validando la máquina de estados.

        Raises:
            ValidationError: si la transición no es válida.
        """
        if not self.can_transition_to(new_status):
            raise ValidationError(
                f'No se puede cambiar de {self.get_status_display()} '
                f'a {dict(self.Status.choices).get(new_status, new_status)}.'
            )
        self.status = new_status

    def __str__(self):
        return f'Solicitud #{self.pk} — {self.get_status_display()}'


class WorkEvidence(models.Model):
    """Foto privada normalizada; evidencia para revisión, no prueba automática."""
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.PROTECT, related_name='evidence')
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    photo = models.FileField(upload_to='work_evidence/')
    caption = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Quote(models.Model):
    """Cotización de un prestador para una solicitud.

    Restricciones (BD-04):
    - Solo puede existir una cotización activa (SUBMITTED) por solicitud.
    - El monto debe ser un entero positivo.
    - El prestador de la cotización debe ser el mismo de la solicitud.
    """

    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Enviada'
        ACCEPTED = 'ACCEPTED', 'Aceptada'
        REJECTED = 'REJECTED', 'Rechazada'
        WITHDRAWN = 'WITHDRAWN', 'Retirada'

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='quotes',
        verbose_name='solicitud',
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quotes',
        limit_choices_to={'role': 'PROVIDER'},
        verbose_name='prestador',
    )
    description = models.TextField('descripción del trabajo incluido')
    price = models.PositiveIntegerField(
        'precio total (CLP)',
        help_text='Monto en pesos chilenos sin decimales.',
    )
    proposed_date = models.DateField('fecha propuesta', null=True, blank=True)
    estimated_duration = models.CharField(
        'duración estimada', max_length=60, blank=True,
    )
    notes = models.TextField('observaciones', blank=True)
    status = models.CharField(
        'estado', max_length=10,
        choices=Status.choices, default=Status.SUBMITTED,
    )
    created_at = models.DateTimeField('creado', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado', auto_now=True)

    class Meta:
        verbose_name = 'cotización'
        verbose_name_plural = 'cotizaciones'
        ordering = ['-created_at']
        # BD-06: índices para cotizaciones
        indexes = [
            models.Index(
                fields=['service_request', 'status'],
                name='idx_quote_request_status',
            ),
        ]
        # SQLite admite índices únicos parciales. La base protege esta regla
        # incluso si dos peticiones superan simultáneamente la validación API.
        constraints = [
            models.UniqueConstraint(
                fields=['service_request'],
                condition=models.Q(status__in=['SUBMITTED', 'ACCEPTED']),
                name='unique_active_quote_per_request',
            ),
            models.CheckConstraint(condition=models.Q(price__gt=0), name='quote_price_positive'),
        ]

    def clean(self):
        """Validaciones a nivel de modelo."""
        # El prestador de la cotización debe ser el de la solicitud
        if (self.service_request_id and self.provider_id
                and self.service_request.provider_id != self.provider_id):
            raise ValidationError(
                'El prestador de la cotización debe ser el asignado a la solicitud.'
            )
        # El precio debe ser positivo
        if self.price is not None and self.price <= 0:
            raise ValidationError({'price': 'El precio debe ser mayor que cero.'})

    def __str__(self):
        return f'Cotización #{self.pk} — ${self.price:,} CLP'


class Rating(models.Model):
    """Valoración del cliente tras completar un servicio (P2 — BE-18).

    Restricciones:
    - Solo el cliente de un servicio completado puede valorar.
    - Solo se permite una valoración por solicitud.
    - El puntaje debe estar entre 1 y 5.
    """

    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name='solicitud',
    )
    score = models.PositiveSmallIntegerField(
        'puntaje',
        help_text='Valor entre 1 y 5.',
    )
    comment = models.TextField('comentario', blank=True)
    created_at = models.DateTimeField('creado', auto_now_add=True)

    class Meta:
        verbose_name = 'valoración'
        verbose_name_plural = 'valoraciones'
        constraints = [models.CheckConstraint(
            condition=models.Q(score__gte=1, score__lte=5), name='rating_score_1_to_5',
        )]

    def clean(self):
        """Valida puntaje y que la solicitud esté completada."""
        if self.score is not None and not (1 <= self.score <= 5):
            raise ValidationError({'score': 'El puntaje debe estar entre 1 y 5.'})
        if (self.service_request_id
                and self.service_request.status != ServiceRequest.Status.COMPLETED):
            raise ValidationError(
                'Solo se puede valorar un servicio completado.'
            )

    def __str__(self):
        return f'Valoración #{self.pk} — {self.score}★'
