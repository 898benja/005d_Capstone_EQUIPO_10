"""Reclamos, reembolsos demo y sanciones con revisión y trazabilidad."""
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from accounts.models import User, ProviderProfile
from services.models import ServiceRequest
from services.workflow import StateConflict
from .models import ServiceDispute, ProviderWarning, PaymentOrder
from .serializers import StrictInput
from .workflow import owned, require_demo


class DisputeInput(StrictInput):
    reason=serializers.CharField(max_length=2000,min_length=10)


class ReviewInput(StrictInput):
    decision=serializers.ChoiceField(choices=['REFUND','REJECT'])
    note=serializers.CharField(max_length=2000,min_length=10)


def read(item):
    return {'id':item.id,'reason':item.reason,'status':item.status,'review_note':item.review_note,
            'created_at':item.created_at,'reviewed_at':item.reviewed_at}


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def dispute(request,pk):
    if request.method=='GET':
        sr=owned(pk,request.user)
        item=ServiceDispute.objects.filter(service_request=sr).first()
        return Response(read(item) if item else None)
    data=DisputeInput(data=request.data);data.is_valid(raise_exception=True)
    with transaction.atomic():
        sr=owned(pk,request.user,client=True,lock=True)
        previous=ServiceDispute.objects.filter(service_request=sr).first()
        if previous:
            return Response(read(previous))
        if not PaymentOrder.objects.filter(service_request=sr,status='DEMO_PAID').exists():
            raise StateConflict('Solo puedes reclamar un servicio con pago aprobado.')
        item=ServiceDispute.objects.create(service_request=sr,**data.validated_data)
    return Response(read(item),status=201)


@transaction.atomic
def resolve(dispute_id,reviewer,decision,note):
    require_demo()
    if not reviewer.is_staff or not reviewer.is_active:
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('Solo administración puede resolver reclamos.')
    item=ServiceDispute.objects.filter(pk=dispute_id).first()
    if not item:
        raise NotFound('Reclamo no encontrado.')
    # El mismo bloqueo por solicitud se comparte con pagos y transiciones.
    ServiceRequest.objects.filter(pk=item.service_request_id).update(updated_at=timezone.now())
    item.refresh_from_db()
    target='REFUNDED' if decision=='REFUND' else 'REJECTED'
    if item.status==target:
        return item
    if item.status!='OPEN':
        raise StateConflict('El reclamo ya tiene una resolución.')
    if decision=='REFUND':
        order=PaymentOrder.objects.filter(service_request_id=item.service_request_id,status='DEMO_PAID').first()
        if not order:
            raise StateConflict('No existe un pago aprobado para reembolsar.')
        order.status='DEMO_REFUNDED';order.refunded_at=timezone.now()
        order.save(update_fields=['status','refunded_at'])
        provider_id=item.service_request.provider_id
        # También serializa reclamos de distintos trabajos del mismo prestador.
        User.objects.filter(pk=provider_id).update(is_active=F('is_active'))
        ProviderWarning.objects.get_or_create(dispute=item,defaults={'provider_id':provider_id})
        if ProviderWarning.objects.filter(provider_id=provider_id).count()>=3:
            User.objects.filter(pk=provider_id).update(is_active=False)
            ProviderProfile.objects.filter(user_id=provider_id).update(is_active=False,map_visible=False)
            Token.objects.filter(user_id=provider_id).delete()
    item.status=target;item.review_note=note;item.reviewed_by=reviewer;item.reviewed_at=timezone.now()
    item.save(update_fields=['status','review_note','reviewed_by','reviewed_at'])
    return item


@api_view(['POST'])
@permission_classes([IsAdminUser])
def review(request,pk):
    data=ReviewInput(data=request.data);data.is_valid(raise_exception=True)
    return Response(read(resolve(pk,request.user,**data.validated_data)))
