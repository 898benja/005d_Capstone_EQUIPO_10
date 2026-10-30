"""Cambios de estado atómicos para el recorrido solicitud → cotización.

SQLite no implementa bloqueos de fila con select_for_update. Por eso la primera
operación de cada transacción es un UPDATE condicionado al estado esperado.
Si otra petición ya lo cambió, se responde 409 sin sobrescribir su decisión.
"""

from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework.exceptions import APIException

from .models import Quote, ServiceRequest


class StateConflict(APIException):
    status_code = 409
    default_detail = 'La solicitud cambió de estado. Actualiza antes de reintentar.'
    default_code = 'conflict'


def _change(request_id, expected, target):
    changed = ServiceRequest.objects.filter(pk=request_id, status__in=expected).update(
        status=target, updated_at=timezone.now(),
    )
    if not changed:
        raise StateConflict()


@transaction.atomic
def create_quote(sr, provider, serializer):
    _change(sr.pk, [ServiceRequest.Status.PENDING], ServiceRequest.Status.QUOTED)
    # Un fallo al insertar revierte también el estado de la solicitud.
    return serializer.save(service_request=sr, provider=provider)


@transaction.atomic
def decide_quote(sr, target):
    request_target = {
        Quote.Status.ACCEPTED: ServiceRequest.Status.ACCEPTED,
        Quote.Status.REJECTED: ServiceRequest.Status.PENDING,
        Quote.Status.WITHDRAWN: ServiceRequest.Status.PENDING,
    }[target]
    try:
        _change(sr.pk, [ServiceRequest.Status.QUOTED], request_target)
    except StateConflict:
        # Repetir la aceptación devuelve el resultado ya confirmado. Rechazar
        # y retirar no se repiten: podría existir una nueva cotización después.
        if target == Quote.Status.ACCEPTED:
            accepted = Quote.objects.filter(
                service_request_id=sr.pk, status=target,
                service_request__status__in=['ACCEPTED', 'IN_PROGRESS', 'COMPLETED'],
            ).first()
            if accepted:
                return accepted
        raise
    quote = Quote.objects.filter(service_request_id=sr.pk, status=Quote.Status.SUBMITTED).first()
    if quote is None:
        raise StateConflict('No hay cotización pendiente para esta solicitud.')
    quote.status = target
    quote.save(update_fields=['status', 'updated_at'])
    return quote


@transaction.atomic
def cancel_request(sr):
    _change(sr.pk, ['PENDING', 'QUOTED'], ServiceRequest.Status.CANCELLED)
    Quote.objects.filter(service_request_id=sr.pk, status=Quote.Status.SUBMITTED).update(
        status=Quote.Status.WITHDRAWN, updated_at=timezone.now(),
    )
    # Refrescar evita serializar el objeto prefetched anterior a la transacción.
    return ServiceRequest.objects.get(pk=sr.pk)


@transaction.atomic
def advance_request(sr, expected, target):
    """Compare-and-set también para inicio y cierre; evita guardar estados viejos."""
    _change(sr.pk, [expected], target)
    from billing.models import PaymentOrder, ServiceDispute
    if not PaymentOrder.objects.filter(service_request=sr,status='DEMO_PAID').exists():
        raise StateConflict('Primero se debe aprobar el pago de demostración.')
    if ServiceDispute.objects.filter(service_request=sr,status='OPEN').exists():
        raise StateConflict('El reclamo está en revisión; no se puede avanzar el servicio.')
    if target=='COMPLETED' and not sr.evidence.exists():
        raise StateConflict('El prestador debe adjuntar al menos una foto del trabajo antes de confirmar.')
    return ServiceRequest.objects.get(pk=sr.pk)


def create_rating(sr, serializer):
    """La restricción única es la autoridad incluso si dos clientes envían a la vez."""
    try:
        with transaction.atomic():
            return serializer.save(service_request=sr)
    except IntegrityError:
        raise StateConflict('Ya existe una valoración para esta solicitud.')
