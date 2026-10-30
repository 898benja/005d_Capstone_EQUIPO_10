"""Billetera exclusivamente demostrativa, sin entrada de PAN ni CVV."""
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from accounts.permissions import IsClient
from .models import DemoCard
from .serializers import StrictInput


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsClient])
def demo_card(request):
    if not (settings.DEBUG and settings.PAYMENTS_DEMO_ENABLED):
        raise PermissionDenied('La billetera de demostración está deshabilitada.')
    if request.method in ('POST', 'DELETE'):
        data = StrictInput(data=request.data)
        data.is_valid(raise_exception=True)
    if request.method == 'DELETE':
        DemoCard.objects.filter(user=request.user).delete()
        return Response(status=204)
    if request.method == 'POST':
        card, _ = DemoCard.objects.get_or_create(user=request.user)
    else:
        card = DemoCard.objects.filter(user=request.user).first()
    # El token permanece en el servidor. Solo se presenta una etiqueta de prueba.
    return Response({'card': {'brand':'DEMO', 'last4':'4242', 'mode':'DEMO'} if card else None})
