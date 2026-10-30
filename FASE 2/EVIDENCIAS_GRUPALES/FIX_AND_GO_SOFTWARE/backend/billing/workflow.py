"""Operaciones serializadas por solicitud para SQLite.

El primer UPDATE adquiere el bloqueo de escritura antes de leer importes.
Toda modificación de materiales y checkout usa este mismo protocolo.
"""
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from services.models import ServiceRequest, Quote
from services.workflow import StateConflict
from .models import MaterialExtra, PaymentOrder, DemoCard


def owned(pk, user, client=False, provider=False, lock=False):
    qs = ServiceRequest.objects.filter(pk=pk)
    # Roles se verifican además de la pertenencia. Staff no ejecuta pagos ajenos.
    if client:
        qs = qs.filter(client=user, client__role='CLIENT')
    elif provider:
        qs = qs.filter(provider=user, provider__role='PROVIDER')
    else:
        from django.db.models import Q
        qs = qs.filter(Q(client=user) | Q(provider=user))
    if lock:
        found = qs.update(updated_at=timezone.now())
        if not found:
            raise NotFound('Solicitud no encontrada.')
    sr = qs.first()
    if sr is None:
        raise NotFound('Solicitud no encontrada.')
    return sr


def require_demo():
    if not (settings.DEBUG and settings.PAYMENTS_DEMO_ENABLED):
        raise PermissionDenied('Pago de demostración deshabilitado. No hay pasarela real configurada.')


def editable(sr):
    if sr.status not in ['ACCEPTED', 'IN_PROGRESS', 'COMPLETED']:
        raise StateConflict('Primero debe existir un servicio aceptado.')
    if PaymentOrder.objects.filter(service_request=sr).exists():
        raise StateConflict('La liquidación ya está congelada; no se pueden modificar materiales.')


@transaction.atomic
def add_material(pk, user, data):
    sr = owned(pk, user, provider=True, lock=True)
    editable(sr)
    return MaterialExtra.objects.create(service_request=sr, **data)


@transaction.atomic
def decide_material(pk, material_id, user, decision):
    sr = owned(pk, user, client=True, lock=True)
    editable(sr)
    item = MaterialExtra.objects.filter(pk=material_id, service_request=sr).first()
    if item is None:
        raise NotFound('Material no encontrado.')
    if item.status == decision:
        return item
    if item.status != 'PENDING':
        raise StateConflict('Este material ya tiene una decisión; no puede modificarse.')
    item.status = decision
    item.decided_at = timezone.now()
    item.save(update_fields=['status', 'decided_at'])
    return item


def amounts(sr):
    quote = Quote.objects.filter(service_request=sr, status='ACCEPTED').first()
    if quote is None:
        raise StateConflict('No hay cotización aceptada.')
    items = list(MaterialExtra.objects.filter(service_request=sr))
    approved = [x for x in items if x.status == 'APPROVED']
    materials = sum(x.quantity * x.unit_price for x in approved)
    total = quote.price + materials
    if total > 2147483647:
        raise ValidationError('El total excede el límite del MVP.')
    rate = settings.DEMO_VAT_PERCENT
    if not 0 <= rate <= 100:
        raise ValidationError('Tasa de demostración inválida.')
    # Los importes existentes son totales CLP: desglosar, nunca sumar IVA dos veces.
    net = int((Decimal(total) * 100 / (100 + rate)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    commission=int((Decimal(quote.price)*Decimal('0.30')).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    return dict(service_amount=quote.price, materials_amount=materials, total=total,
                commission_percent=30, commission_amount=commission, provider_amount=total-commission,
                net_amount=net, vat_amount=total-net, vat_percent=rate,
                snapshot={'quote_id': quote.pk, 'service_description': quote.description,
                          'materials': [{'id': x.pk, 'description': x.description, 'quantity': x.quantity,
                                         'unit_price': x.unit_price, 'total': x.quantity*x.unit_price} for x in approved],
                          'notice': 'DEMOSTRACIÓN SIN COBRO REAL NI VALIDEZ TRIBUTARIA'}), any(x.status == 'PENDING' for x in items)


@transaction.atomic
def checkout(pk, user):
    require_demo()
    sr = owned(pk, user, client=True, lock=True)
    previous = PaymentOrder.objects.filter(service_request=sr).first()
    if previous:
        return previous, False
    if sr.status != 'ACCEPTED':
        raise StateConflict('El pago se confirma después de aceptar la cotización y antes de iniciar el trabajo.')
    values, pending = amounts(sr)
    if pending:
        raise StateConflict('Aprueba o rechaza todos los materiales antes de pagar.')
    return PaymentOrder.objects.create(service_request=sr, **values), True


@transaction.atomic
def demo_result(pk, user, outcome):
    require_demo()
    sr = owned(pk, user, client=True, lock=True)
    order = PaymentOrder.objects.filter(service_request=sr).first()
    if order is None:
        raise NotFound('Primero crea la liquidación.')
    if order.status == 'DEMO_REFUNDED':
        raise StateConflict('Este pago ya fue reembolsado y no puede volver a cobrarse.')
    if order.status == 'DEMO_PAID':
        if outcome != 'approved':
            raise StateConflict('Una aprobación confirmada no puede convertirse en rechazo.')
        return order
    if not DemoCard.objects.filter(user=user).exists():
        raise StateConflict('Guarda primero una tarjeta de demostración en Mi perfil.')
    order.snapshot={**order.snapshot,'card':{'brand':'DEMO','last4':'4242'}}
    order.status = 'DEMO_PAID' if outcome == 'approved' else 'FAILED'
    order.paid_at = timezone.now() if outcome == 'approved' else None
    order.save(update_fields=['status', 'paid_at', 'snapshot'])
    return order
