from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """Permite acceso solo a usuarios con rol CLIENT."""

    message = 'Esta acción está reservada para clientes.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'CLIENT'
        )


class IsProvider(BasePermission):
    """Permite acceso solo a usuarios con rol PROVIDER."""

    message = 'Esta acción está reservada para prestadores.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'PROVIDER'
        )
