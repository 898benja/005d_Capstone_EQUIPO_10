"""Vistas de la app services.

Cubre BE-07 (solicitudes), BE-08 (listado/detalle/cancelación),
BE-09 (cotizaciones), BE-12 (paginación y filtros),
BE-17 (cierre), BE-18 (valoración).
"""

import logging

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsClient, IsProvider
from core.pagination import paginate_queryset
from .models import Quote, Rating, ServiceRequest
from .workflow import cancel_request, create_quote, decide_quote, advance_request, create_rating
from .serializers import (
    QuoteCreateSerializer,
    QuoteReadSerializer,
    RatingCreateSerializer,
    RatingReadSerializer,
    ServiceRequestCreateSerializer,
    ServiceRequestDetailSerializer,
    ServiceRequestListSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_request_or_404(pk, user):
    """Devuelve la solicitud si el usuario tiene acceso, o None.

    BE-04: un tercero no puede acceder a recursos ajenos.
    """
    try:
        sr = ServiceRequest.objects.select_related(
            'client', 'provider', 'category', 'commune',
        ).prefetch_related('quotes').get(pk=pk)
    except ServiceRequest.DoesNotExist:
        return None
    # Solo el cliente, el prestador o staff pueden ver la solicitud
    if user.id == sr.client_id or user.id == sr.provider_id or user.is_staff:
        return sr
    return None


def _error(detail, code=status.HTTP_400_BAD_REQUEST):
    """BE-11: respuesta de error normalizada con código y mensaje."""
    return Response(
        {'code': 'error', 'detail': detail},
        status=code,
    )


def _conflict(detail):
    """Respuesta 409 normalizada."""
    return Response(
        {'code': 'conflict', 'detail': detail},
        status=status.HTTP_409_CONFLICT,
    )


def _forbidden(detail):
    """Respuesta 403 normalizada."""
    return Response(
        {'code': 'forbidden', 'detail': detail},
        status=status.HTTP_403_FORBIDDEN,
    )


def _not_found(detail='Solicitud no encontrada.'):
    """Respuesta 404 normalizada."""
    return Response(
        {'code': 'not_found', 'detail': detail},
        status=status.HTTP_404_NOT_FOUND,
    )


# ---------------------------------------------------------------------------
# Solicitudes (BE-07, BE-08, BE-12)
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def request_list_create(request):
    """GET: listar solicitudes del usuario. POST: crear solicitud (solo cliente).

    GET soporta filtros opcionales (BE-12):
    - ?status=PENDING,QUOTED  (filtrar por estado, separados por coma)
    - ?category=<id>          (filtrar por categoría)
    - ?commune=<id>           (filtrar por comuna)
    - ?provider=<id>          (filtrar por prestador — solo si es el propio)
    - ?date_from=YYYY-MM-DD   (solicitudes desde esta fecha)
    - ?date_to=YYYY-MM-DD     (solicitudes hasta esta fecha)
    - ?page=1&page_size=20    (paginación)

    BE-12: paginación aplicada a la respuesta (20 resultados por defecto).
    """
    if request.method == 'POST':
        if request.user.role != 'CLIENT':
            return _forbidden('Solo los clientes pueden crear solicitudes.')

        serializer = ServiceRequestCreateSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        sr = serializer.save()

        logger.info(
            'Solicitud #%d creada por cliente #%d al prestador #%d',
            sr.pk, sr.client_id, sr.provider_id,
        )

        return Response(
            ServiceRequestDetailSerializer(sr, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    # GET — filtrar según rol (BE-08)
    if request.user.role == 'CLIENT':
        qs = ServiceRequest.objects.filter(client=request.user)
    elif request.user.role == 'PROVIDER':
        qs = ServiceRequest.objects.filter(provider=request.user)
    else:
        qs = ServiceRequest.objects.none()

    from .filters import RequestFilters
    filters = RequestFilters(data=request.query_params)
    filters.is_valid(raise_exception=True)

    # Filtros opcionales (BE-12)
    status_filter = request.query_params.get('status')
    if status_filter:
        statuses = [s.strip() for s in status_filter.split(',') if s.strip()]
        valid_statuses = {choice[0] for choice in ServiceRequest.Status.choices}
        statuses = [s for s in statuses if s in valid_statuses]
        if statuses:
            qs = qs.filter(status__in=statuses)

    category_filter = request.query_params.get('category')
    if category_filter:
        qs = qs.filter(category_id=category_filter)

    commune_filter = request.query_params.get('commune')
    if commune_filter:
        qs = qs.filter(commune_id=commune_filter)

    date_from = request.query_params.get('date_from')
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)

    date_to = request.query_params.get('date_to')
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    qs = qs.select_related('client', 'provider', 'category', 'commune')
    qs = qs.prefetch_related('quotes')

    # Orden estable por defecto: más recientes primero (BE-12)
    if filters.validated_data.get('provider'):
        qs = qs.filter(provider_id=filters.validated_data['provider'])
    qs = qs.order_by('-created_at', '-pk')

    return paginate_queryset(request, qs, ServiceRequestListSerializer)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def request_detail(request, pk):
    """Detalle de una solicitud."""
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()
    return Response(
        ServiceRequestDetailSerializer(sr, context={'request': request}).data,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def request_cancel(request, pk):
    """Cancelar una solicitud (solo cliente propietario, si no está aceptada).

    BE-08: el cliente cancela solo antes de aceptar.
    Usa la máquina de estados de ServiceRequest (BD-03).
    """
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()

    if sr.client_id != request.user.id:
        return _forbidden('Solo el cliente propietario puede cancelar esta solicitud.')

    sr = cancel_request(sr)

    logger.info(
        'Solicitud #%d cancelada por cliente #%d',
        sr.pk, request.user.id,
    )

    return Response(
        ServiceRequestDetailSerializer(sr, context={'request': request}).data,
    )


# ---------------------------------------------------------------------------
# Cotizaciones (BE-09)
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def quote_create_or_get(request, pk):
    """
    GET: ver cotización activa de la solicitud.
    POST: crear cotización (solo prestador asignado).

    BE-09: una sola cotización activa, monto positivo, idempotencia.
    """
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()

    if request.method == 'GET':
        quote = sr.quotes.filter(
            status__in=[Quote.Status.SUBMITTED, Quote.Status.ACCEPTED],
        ).first()
        if quote is None:
            return _not_found('No hay cotización para esta solicitud.')
        return Response(QuoteReadSerializer(quote).data)

    # POST — crear cotización
    if request.user.role != 'PROVIDER':
        return _forbidden('Solo los prestadores pueden cotizar.')

    if sr.provider_id != request.user.id:
        return _forbidden('Solo el prestador asignado puede cotizar esta solicitud.')

    serializer = QuoteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    quote = create_quote(sr, request.user, serializer)

    logger.info(
        'Cotización #%d creada por prestador #%d para solicitud #%d — $%s CLP',
        quote.pk, request.user.id, sr.pk, f'{quote.price:,}',
    )

    return Response(QuoteReadSerializer(quote).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def quote_accept(request, pk):
    """Aceptar la cotización de una solicitud (solo cliente propietario).

    BE-09: aceptación transaccional.
    """
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()

    if sr.client_id != request.user.id:
        return _forbidden('Solo el cliente propietario puede aceptar.')

    quote = decide_quote(sr, Quote.Status.ACCEPTED)

    logger.info(
        'Cotización #%d aceptada por cliente #%d (solicitud #%d)',
        quote.pk, request.user.id, sr.pk,
    )

    return Response(QuoteReadSerializer(quote).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def quote_reject(request, pk):
    """Rechazar la cotización de una solicitud (solo cliente propietario).

    BE-09: rechazo transaccional; la solicitud vuelve a PENDING
    para permitir nueva cotización.
    """
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()

    if sr.client_id != request.user.id:
        return _forbidden('Solo el cliente propietario puede rechazar.')

    quote = decide_quote(sr, Quote.Status.REJECTED)

    logger.info(
        'Cotización #%d rechazada por cliente #%d (solicitud #%d)',
        quote.pk, request.user.id, sr.pk,
    )

    return Response(QuoteReadSerializer(quote).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsProvider])
def quote_withdraw(request, pk):
    """Retirar la cotización (solo prestador asignado, si aún está pendiente).

    BE-09: retiro permitido, la solicitud vuelve a PENDING.
    """
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()

    if sr.provider_id != request.user.id:
        return _forbidden('Solo el prestador asignado puede retirar la cotización.')

    quote = decide_quote(sr, Quote.Status.WITHDRAWN)

    logger.info(
        'Cotización #%d retirada por prestador #%d (solicitud #%d)',
        quote.pk, request.user.id, sr.pk,
    )

    return Response(QuoteReadSerializer(quote).data)


# ---------------------------------------------------------------------------
# Cierre de servicio (P2 — BE-17)
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsProvider])
def request_start(request, pk):
    """Iniciar servicio — solo prestador asignado tras aceptar cotización.

    BE-17: transición ACCEPTED → IN_PROGRESS.
    """
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()

    if sr.provider_id != request.user.id:
        return _forbidden('Solo el prestador asignado puede iniciar el servicio.')

    if not sr.can_transition_to(ServiceRequest.Status.IN_PROGRESS):
        return _conflict(
            f'No se puede iniciar un servicio en estado {sr.get_status_display()}.'
        )

    sr = advance_request(sr, ServiceRequest.Status.ACCEPTED, ServiceRequest.Status.IN_PROGRESS)

    logger.info(
        'Servicio de solicitud #%d iniciado por prestador #%d',
        sr.pk, request.user.id,
    )

    return Response(
        ServiceRequestDetailSerializer(sr, context={'request': request}).data,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_complete(request, pk):
    """Completar servicio — prestador o cliente pueden marcar como completado.

    BE-17: transición IN_PROGRESS → COMPLETED.
    """
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()

    # Solo las partes involucradas pueden completar
    if request.user.id != sr.client_id:
        return _forbidden('Solo el cliente puede confirmar que el trabajo fue realizado.')

    if not sr.can_transition_to(ServiceRequest.Status.COMPLETED):
        return _conflict(
            f'No se puede completar un servicio en estado {sr.get_status_display()}.'
        )

    sr = advance_request(sr, ServiceRequest.Status.IN_PROGRESS, ServiceRequest.Status.COMPLETED)

    logger.info(
        'Servicio de solicitud #%d completado (marcado por usuario #%d)',
        sr.pk, request.user.id,
    )

    return Response(
        ServiceRequestDetailSerializer(sr, context={'request': request}).data,
    )


# ---------------------------------------------------------------------------
# Valoraciones (P2 — BE-18)
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def request_rating(request, pk):
    """GET: ver valoración. POST: crear valoración (solo cliente del servicio completado).

    BE-18: solo una valoración por solicitud, solo si COMPLETED.
    """
    sr = _get_request_or_404(pk, request.user)
    if sr is None:
        return _not_found()

    if request.method == 'GET':
        try:
            rating = sr.rating
        except Rating.DoesNotExist:
            return _not_found('No hay valoración para esta solicitud.')
        return Response(RatingReadSerializer(rating).data)

    # POST — crear valoración
    if request.user.id != sr.client_id:
        return _forbidden('Solo el cliente puede valorar el servicio.')

    if sr.status != ServiceRequest.Status.COMPLETED:
        return _error('Solo se puede valorar un servicio completado.')

    # BE-18: solo una valoración por solicitud
    if Rating.objects.filter(service_request=sr).exists():
        return _conflict('Ya existe una valoración para esta solicitud.')

    serializer = RatingCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    rating = create_rating(sr, serializer)

    logger.info(
        'Valoración de solicitud #%d creada por cliente #%d — %d★',
        sr.pk, request.user.id, rating.score,
    )

    return Response(RatingReadSerializer(rating).data, status=status.HTTP_201_CREATED)
