"""Autenticación con token que expira (BE-03).

Extiende TokenAuthentication de DRF para invalidar tokens después de
TOKEN_EXPIRY_HOURS (por defecto 24h). Si el token expiró, se elimina
automáticamente y se retorna 401.
"""

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


def token_is_expired(token):
    """Indica si un token superó la duración configurada."""
    hours = getattr(settings, 'TOKEN_EXPIRY_HOURS', 24)
    return timezone.now() > token.created + timedelta(hours=hours)


class ExpiringTokenAuthentication(TokenAuthentication):
    """Token que expira después de TOKEN_EXPIRY_HOURS horas.

    BE-03: tokens con duración definida para el MVP.
    """

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed('Token inválido.')

        if not token.user.is_active:
            raise AuthenticationFailed('Cuenta de usuario desactivada.')

        # Verificar expiración
        if token_is_expired(token):
            token.delete()
            raise AuthenticationFailed('Token expirado. Inicia sesión nuevamente.')

        return (token.user, token)
