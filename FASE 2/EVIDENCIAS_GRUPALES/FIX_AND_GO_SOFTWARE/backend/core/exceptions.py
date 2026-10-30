"""Manejador de excepciones personalizado para la API (BE-11).

Define una estructura de error consistente:
{
    "code": "error" | "validation_error" | "not_found" | "forbidden" | ...,
    "detail": "mensaje legible" | { campo: ["errores"] },
}

El frontend puede presentar errores sin analizar formatos distintos por endpoint.
"""

import logging

from rest_framework.views import exception_handler, set_rollback
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


# Mapeo de códigos HTTP a códigos de error de la API
STATUS_CODE_MAP = {
    status.HTTP_400_BAD_REQUEST: 'validation_error',
    status.HTTP_401_UNAUTHORIZED: 'unauthorized',
    status.HTTP_403_FORBIDDEN: 'forbidden',
    status.HTTP_404_NOT_FOUND: 'not_found',
    status.HTTP_405_METHOD_NOT_ALLOWED: 'method_not_allowed',
    status.HTTP_409_CONFLICT: 'conflict',
    status.HTTP_429_TOO_MANY_REQUESTS: 'throttled',
    status.HTTP_500_INTERNAL_SERVER_ERROR: 'server_error',
}


def custom_exception_handler(exc, context):
    """Manejador que normaliza todas las respuestas de error de DRF.

    Garantiza que todas las respuestas de error tengan la estructura:
    {
        "code": str,
        "detail": str | dict,
    }
    """
    response = exception_handler(exc, context)

    if response is None:
        # No devolver HTML de DEBUG, trazas ni valores privados de excepciones.
        # Las transacciones de negocio ya se deshicieron al salir del servicio.
        set_rollback()
        logger.error('Error no manejado en API: %s', type(exc).__name__)
        return Response({'code': 'server_error', 'detail': 'No se pudo completar la operación. Intenta nuevamente.'}, status=500)

    # Obtener código de error semántico
    error_code = STATUS_CODE_MAP.get(response.status_code, 'error')

    # Si la respuesta ya tiene la estructura normalizada, no modificar
    if isinstance(response.data, dict) and 'code' in response.data:
        return response

    # Normalizar la estructura del error
    original_data = response.data

    if isinstance(original_data, dict):
        # Si tiene 'detail' es un error simple de DRF
        if 'detail' in original_data and len(original_data) == 1:
            response.data = {
                'code': error_code,
                'detail': str(original_data['detail']),
            }
        # Si tiene 'non_field_errors', extraer como detail
        elif 'non_field_errors' in original_data:
            errors = original_data.pop('non_field_errors')
            detail = errors[0] if len(errors) == 1 else errors
            # Si quedan otros campos, incluirlos como errores de campo
            if original_data:
                response.data = {
                    'code': error_code,
                    'detail': detail,
                    'field_errors': original_data,
                }
            else:
                response.data = {
                    'code': error_code,
                    'detail': detail,
                }
        else:
            # Errores de validación por campo
            response.data = {
                'code': error_code,
                'detail': original_data,
            }
    elif isinstance(original_data, list):
        # Lista de errores (poco común, pero posible)
        response.data = {
            'code': error_code,
            'detail': original_data[0] if len(original_data) == 1 else original_data,
        }

    return response
