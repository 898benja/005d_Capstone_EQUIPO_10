"""Webpay Plus integration ONLY. Production hosts/credentials are not accepted.

The browser return is not proof of payment. Only the server-to-server commit,
matching amount and purchase order, can unlock work and conversation.
"""
import json
import secrets
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.response import Response
from .models import WebpayAttempt, PaymentOrder
from .workflow import checkout, owned
from .serializers import StrictInput
from services.workflow import StateConflict

BASE = 'https://webpay3gint.transbank.cl'
ENDPOINT = BASE + '/rswebpaytransaction/api/webpay/v1.2/transactions'
# Public integration credentials published by Transbank, not merchant secrets.
HEADERS = {'Tbk-Api-Key-Id': '597055555532',
           'Tbk-Api-Key-Secret': '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
           'Content-Type': 'application/json'}


class GatewayUnavailable(APIException):
    status_code = 503
    default_detail = 'Webpay de prueba no respondió. Conservamos tu solicitud; vuelve a intentarlo.'


def enabled():
    return bool(settings.DEBUG and settings.PAYMENTS_DEMO_ENABLED and
                settings.WEBPAY_INTEGRATION_ENABLED and settings.WEBPAY_RETURN_URL)


def call(method, suffix='', body=None):
    req = Request(ENDPOINT + suffix, headers=HEADERS, method=method,
                  data=json.dumps(body).encode() if body is not None else None)
    try:
        with urlopen(req, timeout=15) as response:
            value = json.load(response)
        if not isinstance(value, dict):
            raise ValueError('Invalid response')
        return value
    except (URLError, TimeoutError, ValueError, OSError):
        # Never leak payment tokens or gateway payloads into user errors/logs.
        raise GatewayUnavailable() from None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def start(request, pk):
    if not enabled():
        raise PermissionDenied('Webpay de integración no está habilitado.')
    data = StrictInput(data=request.data); data.is_valid(raise_exception=True)
    sr = owned(pk, request.user, client=True, lock=True)
    if sr.status != 'ACCEPTED':
        raise StateConflict('Acepta la cotización antes de pagar.')
    order, _ = checkout(pk, request.user)
    if order.status in ['DEMO_PAID', 'DEMO_REFUNDED']:
        raise StateConflict('El pago ya tiene un resultado definitivo.')
    attempt = order.webpay_attempts.filter(finished=False).first()
    if not attempt:
        buy_order = 'fg-' + secrets.token_hex(10)
        result = call('POST', body={'buy_order': buy_order, 'session_id': str(order.pk),
                                  'amount': order.total, 'return_url': settings.WEBPAY_RETURN_URL})
        token = result.get('token', '')
        if not isinstance(token, str) or not token.isalnum() or len(token) > 128 or not token:
            raise GatewayUnavailable()
        # This integration supports only the official hosted integration form.
        if urlsplit(result.get('url', '')).hostname != 'webpay3gint.transbank.cl':
            raise GatewayUnavailable()
        attempt = WebpayAttempt.objects.create(order=order, buy_order=buy_order, token=token)
    order.mode = 'WEBPAY_INT'; order.status = 'PENDING'
    order.save(update_fields=['mode', 'status'])
    origin = settings.WEBPAY_RETURN_URL.rsplit('/webpay/return/', 1)[0]
    return Response({'url': origin + '/webpay/launch/?' + urlencode({'token': attempt.token})})


def page(title, detail, status=200, attempt=None, approved=False):
    order = attempt.order if attempt else None
    money = lambda amount: '$' + f'{amount:,}'.replace(',', '.')
    result = HttpResponse(render_to_string('billing/payment.html', {
        'title': title, 'detail': detail, 'attempt': attempt, 'approved': approved,
        'total': money(order.total) if order else None,
        'service': money(order.service_amount) if order else None,
        'materials': money(order.materials_amount) if order else None,
        'app_url': settings.WEBPAY_APP_URL,
    }), status=status)
    result['Cache-Control'] = 'no-store'
    result['Referrer-Policy'] = 'no-referrer'
    result['Content-Security-Policy'] = "default-src 'none'; style-src 'unsafe-inline'; form-action https://webpay3gint.transbank.cl; frame-ancestors 'none'; base-uri 'none'"
    return result


@require_http_methods(['GET'])
def launch(request):
    if not enabled(): return page('Pago deshabilitado', 'Contacta al equipo del MVP.', 403)
    attempt = WebpayAttempt.objects.filter(token=request.GET.get('token', ''), finished=False).first()
    if not attempt: return page('Sesión no disponible', 'Regresa a la solicitud para revisar el pago.', 404)
    return page('Todo listo para pagar', 'Revisa el total. Al continuar abrirás el formulario oficial de Transbank.', attempt=attempt)


@csrf_exempt  # External return: token possession + server verification, never session authority.
@require_http_methods(['GET', 'POST'])
def returned(request):
    if not enabled(): return page('Pago deshabilitado', 'Contacta al equipo del MVP.', 403)
    data = request.POST if request.method == 'POST' else request.GET
    token = data.get('token_ws') or data.get('TBK_TOKEN', '')
    attempt = WebpayAttempt.objects.filter(token=token).first() if token else None
    # Timeout returns purchase order and session, without token. Gateway status
    # is still verified server to server; browser parameters cannot approve it.
    if not token:
        session_id = data.get('TBK_ID_SESION') or data.get('TBK_ID_SESSION', '')
        if session_id.isdigit():
            attempt = WebpayAttempt.objects.filter(buy_order=data.get('TBK_ORDEN_COMPRA', ''), order_id=int(session_id)).first()
            if attempt:
                token = attempt.token
    if not attempt: return page('Sesión desconocida', 'No se modificó ningún pago.', 404)
    try:
        with transaction.atomic():
            order = attempt.order
            from services.models import ServiceRequest
            ServiceRequest.objects.filter(pk=order.service_request_id).update(updated_at=timezone.now())
            attempt.refresh_from_db(); order.refresh_from_db()
            if not attempt.finished:
                # A repeated callback or interrupted commit is reconciled via status.
                result = call('GET', '/' + token)
                if result.get('status') == 'INITIALIZED' and data.get('token_ws') and not data.get('TBK_TOKEN'):
                    result = call('PUT', '/' + token, {})
                approved = (result.get('status') == 'AUTHORIZED' and result.get('response_code') == 0
                            and result.get('amount') == order.total and result.get('buy_order') == attempt.buy_order)
                if approved and order.service_request.status == 'ACCEPTED' and order.status != 'DEMO_REFUNDED':
                    order.status = 'DEMO_PAID'; order.paid_at = timezone.now()
                    order.save(update_fields=['status', 'paid_at'])
                elif order.status not in ['DEMO_PAID', 'DEMO_REFUNDED']:
                    order.status = 'FAILED'; order.save(update_fields=['status'])
                attempt.finished = True; attempt.save(update_fields=['finished'])
        return page('Pago de prueba aprobado' if order.status == 'DEMO_PAID' else 'Pago no aprobado',
                    'El estado fue verificado con Transbank. Vuelve a tu solicitud para continuar.', approved=order.status == 'DEMO_PAID')
    except GatewayUnavailable:
        return page('Verificación pendiente', 'No repitas el pago. Recarga esta página para verificar el resultado.', 503)
