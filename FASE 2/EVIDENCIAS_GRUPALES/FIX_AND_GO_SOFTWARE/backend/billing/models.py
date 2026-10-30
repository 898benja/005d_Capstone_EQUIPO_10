"""Materiales aprobados y liquidación final del MVP.

Importes enteros en CLP, con IVA incluido en los precios de demostración.
Nunca guardar PAN, CVV, contraseñas bancarias o tarjetas en estos modelos.
"""
from django.conf import settings
from django.db import models
import uuid


class DemoCard(models.Model):
    """Referencia ficticia. No recibe ni representa una tarjeta bancaria real."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MaterialExtra(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING'
        APPROVED = 'APPROVED'
        REJECTED = 'REJECTED'
    service_request = models.ForeignKey('services.ServiceRequest', on_delete=models.PROTECT, related_name='material_extras')
    description = models.CharField(max_length=240)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=1, quantity__lte=10000), name='material_quantity_range'),
            models.CheckConstraint(condition=models.Q(unit_price__gte=1, unit_price__lte=100000000), name='material_price_range'),
        ]

class PaymentOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING'
        DEMO_PAID = 'DEMO_PAID'
        FAILED = 'FAILED'
        DEMO_REFUNDED = 'DEMO_REFUNDED'
    # One final collection per service. Snapshot remains immutable after checkout.
    service_request = models.OneToOneField('services.ServiceRequest', on_delete=models.PROTECT, related_name='payment_order')
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    mode = models.CharField(max_length=10, default='DEMO', editable=False)
    service_amount = models.PositiveIntegerField()
    materials_amount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    net_amount = models.PositiveIntegerField()
    vat_amount = models.PositiveIntegerField()
    vat_percent = models.PositiveSmallIntegerField()
    commission_percent = models.PositiveSmallIntegerField(default=0)
    commission_amount = models.PositiveIntegerField(default=0)
    provider_amount = models.PositiveIntegerField(default=0)
    snapshot = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True)
    refunded_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(total__gt=0), name='payment_total_positive')]

class ServiceMessage(models.Model):
    """Mensajería interna de demostración, sin enlace ni publicación de teléfonos."""
    service_request = models.ForeignKey('services.ServiceRequest', on_delete=models.PROTECT, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    text = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['id']


class ServiceDispute(models.Model):
    """Un reclamo no sanciona: exige una resolución administrativa registrada."""
    service_request = models.OneToOneField('services.ServiceRequest', on_delete=models.PROTECT, related_name='dispute')
    reason = models.CharField(max_length=2000)
    status = models.CharField(max_length=16, choices=[('OPEN','En revisión'),('REJECTED','Rechazado'),('REFUNDED','Reembolsado demo')], default='OPEN')
    review_note = models.CharField(max_length=2000, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, related_name='reviewed_disputes')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True)


class ProviderWarning(models.Model):
    dispute = models.OneToOneField(ServiceDispute, on_delete=models.PROTECT)
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='service_warnings')
    created_at = models.DateTimeField(auto_now_add=True)
