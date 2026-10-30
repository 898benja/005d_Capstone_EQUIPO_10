"""Miniatura pública elegida por el prestador; nunca aceptar URLs externas."""
import base64
import io
from PIL import Image, ImageOps
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .permissions import IsProvider
from .models import ProviderProfile
from services.evidence import EvidenceInput, normalize
from billing.serializers import StrictInput


@api_view(['POST','DELETE'])
@permission_classes([IsProvider])
def avatar(request):
    profile=get_object_or_404(ProviderProfile,user=request.user)
    serializer=(EvidenceInput if request.method=='POST' else StrictInput)(data=request.data)
    serializer.is_valid(raise_exception=True)
    value=''
    if request.method=='POST':
        image=Image.open(io.BytesIO(normalize(serializer.validated_data['image_base64'])))
        image=ImageOps.fit(image,(240,240))
        output=io.BytesIO();image.save(output,format='JPEG',quality=80)
        value='data:image/jpeg;base64,'+base64.b64encode(output.getvalue()).decode()
    ProviderProfile.objects.filter(pk=profile.pk).update(avatar=value)
    return Response({'avatar':value})
