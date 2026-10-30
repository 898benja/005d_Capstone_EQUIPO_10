"""Endpoints del flujo final. Ninguna respuesta representa un cobro bancario real."""
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from core.pagination import paginate_queryset
from . import workflow
from .models import MaterialExtra, PaymentOrder, ServiceMessage
from .serializers import (MaterialInput, DecisionInput, DemoResultInput, MaterialRead,
                          PaymentRead, MessageInput, MessageRead, StrictInput)


def validated(cls, data):
    serializer = cls(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def materials(request, pk):
    if request.method == 'POST':
        item = workflow.add_material(pk, request.user, validated(MaterialInput, request.data))
        return Response(MaterialRead(item).data, status=201)
    sr = workflow.owned(pk, request.user)
    return paginate_queryset(request, MaterialExtra.objects.filter(service_request=sr), MaterialRead)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decision(request, pk, material_id):
    data = validated(DecisionInput, request.data)
    item = workflow.decide_material(pk, material_id, request.user, data['decision'])
    return Response(MaterialRead(item).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary(request, pk):
    sr = workflow.owned(pk, request.user)
    order = PaymentOrder.objects.filter(service_request=sr).first()
    if order:
        return Response({**PaymentRead(order).data, 'demo_enabled': settings.DEBUG and settings.PAYMENTS_DEMO_ENABLED})
    values, pending = workflow.amounts(sr)
    return Response({**values, 'currency': 'CLP', 'mode': 'DEMO', 'status': 'DRAFT',
                     'has_pending_materials': pending, 'fiscal_document': False,
                     'demo_enabled': settings.DEBUG and settings.PAYMENTS_DEMO_ENABLED})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request, pk):
    validated(StrictInput, request.data)  # El cliente no controla importes ni estados.
    order, created = workflow.checkout(pk, request.user)
    return Response(PaymentRead(order).data, status=201 if created else 200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_result(request, pk):
    data = validated(DemoResultInput, request.data)
    order = workflow.demo_result(pk, request.user, data['outcome'])
    return Response(PaymentRead(order).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def receipt(request, pk):
    sr = workflow.owned(pk, request.user)
    order = PaymentOrder.objects.filter(service_request=sr, status__in=['DEMO_PAID','DEMO_REFUNDED']).first()
    if not order:
        raise NotFound('No hay comprobante de demostración aprobado.')
    return Response({'title': 'Comprobante de demostración — no es boleta', **PaymentRead(order).data})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def messages(request, pk):
    # Restricción literal solicitada: conversación disponible después del pago demo.
    # No implica protección contra contactos escritos en campos libres o fuera de la app.
    sr = workflow.owned(pk, request.user, lock=request.method=='POST')
    if not PaymentOrder.objects.filter(service_request=sr, status='DEMO_PAID').exists():
        raise PermissionDenied('La conversación se habilita tras el pago de demostración.')
    if request.method == 'POST':
        data = validated(MessageInput, request.data)
        item = ServiceMessage.objects.create(service_request=sr, sender=request.user, **data)
        return Response(MessageRead(item).data, status=201)
    return paginate_queryset(request, ServiceMessage.objects.filter(service_request=sr), MessageRead)
