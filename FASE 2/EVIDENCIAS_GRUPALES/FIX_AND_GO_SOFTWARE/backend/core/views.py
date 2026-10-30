"""Vistas de diagnóstico técnico (BE-16).

Incluye health check con verificación de base de datos y timestamps.
"""

import logging

from django.conf import settings
from django.db import connection, DatabaseError
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request):
    """Health check de la API.

    BE-16: comprobación de base de datos con diagnóstico.
    Permite identificar fallas de configuración, red o base
    durante la presentación.
    """
    db_ok = False
    db_error = None

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        db_ok = True
    except DatabaseError as e:
        db_error = str(type(e).__name__)
        logger.error(
            'Health check: falla de base de datos — %s',
            db_error,
        )

    response_data = {
        'status': 'ok' if db_ok else 'unavailable',
        'service': 'fix-and-go-api',
        'database': 'ok' if db_ok else 'unavailable',
        'timestamp': timezone.now().isoformat(),
        'debug': settings.DEBUG,
    }

    # BE-16: incluir el tipo de error (sin detalles privados) en modo debug
    if not db_ok and settings.DEBUG and db_error:
        response_data['db_error_type'] = db_error

    status_code = 200 if db_ok else 503
    return Response(response_data, status=status_code)
