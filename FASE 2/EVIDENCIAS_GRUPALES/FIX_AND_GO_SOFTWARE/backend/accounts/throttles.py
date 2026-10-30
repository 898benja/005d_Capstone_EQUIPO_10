"""Throttling (control de intentos) para autenticación (BE-03).

Limita intentos de login y registro para prevenir abuso.
Configuración conservadora para MVP: 10 intentos/minuto en login,
20 en registro.
"""

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Limita intentos de login por IP.

    BE-03: prevenir ataques de fuerza bruta.
    """
    scope = 'login'
    rate = '10/min'


class RegisterRateThrottle(AnonRateThrottle):
    """Limita intentos de registro por IP.

    BE-03: prevenir spam de cuentas.
    """
    scope = 'register'
    rate = '20/min'
