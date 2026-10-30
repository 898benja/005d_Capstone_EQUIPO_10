"""Fotos privadas con límites y eliminación de metadatos EXIF."""
import base64
import binascii
import io
import uuid
from PIL import Image, ImageOps, UnidentifiedImageError
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from billing.workflow import owned
from billing.serializers import StrictInput
from .models import WorkEvidence


class EvidenceInput(StrictInput):
    image_base64 = serializers.CharField(max_length=2800000, trim_whitespace=False)
    caption = serializers.CharField(max_length=240, required=False, allow_blank=True)


def normalize(raw):
    try:
        binary = base64.b64decode(raw, validate=True)
        if len(binary)>2*1024*1024:
            raise ValueError('size')
        with Image.open(io.BytesIO(binary)) as image:
            if image.format not in ('JPEG','PNG','WEBP') or image.width*image.height>16000000:
                raise ValueError('image')
            image.load()
            image=ImageOps.exif_transpose(image).convert('RGB')
            image.thumbnail((1600,1600))
            clean=Image.new('RGB',image.size)
            clean.paste(image)
            output=io.BytesIO()
            clean.save(output,format='JPEG',quality=85)
            return output.getvalue()
    except (ValueError, binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValidationError('Adjunta una foto JPEG, PNG o WebP de hasta 2 MB y 16 megapíxeles.')


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def evidence(request,pk):
    if request.method=='GET':
        sr=owned(pk,request.user)
        return Response(list(sr.evidence.order_by('id').values('id','caption','created_at')))
    serializer=EvidenceInput(data=request.data)
    serializer.is_valid(raise_exception=True)
    owned(pk,request.user,provider=True)
    image=normalize(serializer.validated_data['image_base64'])
    saved=None
    try:
        with transaction.atomic():
            sr=owned(pk,request.user,provider=True,lock=True)
            from billing.models import PaymentOrder
            if PaymentOrder.objects.filter(service_request=sr,status='DEMO_REFUNDED').exists():
                raise ValidationError('El caso reembolsado está cerrado; conserva sus evidencias.')
            if sr.status not in ('IN_PROGRESS','COMPLETED'):
                raise ValidationError('Las fotos se agregan durante o después del trabajo.')
            if sr.evidence.count()>=10:
                raise ValidationError('Máximo 10 fotos por trabajo.')
            saved=WorkEvidence(service_request=sr,uploader=request.user,caption=serializer.validated_data.get('caption',''))
            saved.photo.save(f'{uuid.uuid4().hex}.jpg',ContentFile(image),save=False)
            saved.save()
        return Response({'id':saved.id,'caption':saved.caption,'created_at':saved.created_at},status=201)
    except Exception:
        if saved and saved.photo.name:
            saved.photo.delete(save=False)
        raise


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evidence_photo(request,pk,evidence_id):
    sr=owned(pk,request.user)
    item=WorkEvidence.objects.filter(service_request=sr,pk=evidence_id).first()
    if not item:
        raise NotFound('Foto no encontrada.')
    with item.photo.open('rb') as file:
        encoded=base64.b64encode(file.read()).decode('ascii')
    response=Response({'image_base64':encoded,'content_type':'image/jpeg'})
    response['Cache-Control']='private, no-store'
    return response
