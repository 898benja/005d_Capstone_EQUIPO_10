"""Vistas de la app accounts.

Cubre BE-02 (registro/login), BE-03 (token/logout), BE-04 (permisos),
BE-05 (perfil prestador).
"""

import logging
from django.db import transaction, IntegrityError
from django.db.models import F

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from .throttles import LoginRateThrottle, RegisterRateThrottle
from rest_framework.response import Response

from .authentication import token_is_expired
from .models import User
from .profile import PersonalProfileSerializer
from .serializers import (
    LoginSerializer,
    ProviderProfileReadSerializer,
    ProviderProfileWriteSerializer,
    RegisterSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Registro e inicio de sesión (BE-02)
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterRateThrottle])
def register_view(request):
    """Registro de nuevo usuario con rol CLIENT o PROVIDER.

    Retorna token y datos del usuario para iniciar sesión inmediata.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, token = serializer.save()
    except IntegrityError:
        # La restricción única cubre dos registros simultáneos del mismo correo.
        if User.objects.filter(email__iexact=serializer.validated_data['email']).exists():
            return Response({'code': 'conflict', 'detail': 'Ya existe una cuenta con este correo electrónico.'}, status=409)
        raise

    logger.info(
        'Nuevo usuario registrado: #%d — rol: %s',
        user.pk, user.role,
    )

    return Response(
        {
            'token': token.key,
            'user': UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    """Inicio de sesión con correo y contraseña.

    BE-02: devuelve token para sesión persistente.
    BE-03: reutiliza token existente o crea uno nuevo.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    # Rotar un token vencido evita entregar una credencial que fallará
    # inmediatamente en la siguiente petición autenticada.
    with transaction.atomic():
        User.objects.filter(pk=user.pk).update(last_login=F('last_login'))
        token = Token.objects.filter(user=user).first()
        if token is None or token_is_expired(token):
            if token is not None:
                token.delete()
            token = Token.objects.create(user=user)

    logger.info('Login exitoso: usuario #%d', user.pk)

    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Cierra sesión eliminando el token actual.

    BE-03: después de cerrar sesión, el token no permite usar la API.
    """
    if hasattr(request.auth, 'delete'):
        request.auth.delete()
    else:
        Token.objects.filter(user=request.user).delete()

    logger.info('Logout: usuario #%d', request.user.id)

    return Response({'detail': 'Sesión cerrada.'})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Devuelve los datos del usuario autenticado.

    BE-02: el frontend usa este endpoint para verificar la sesión.
    BE-03: si el token es inválido, DRF retorna 401 automáticamente.
    """
    if request.method == 'PATCH':
        serializer = PersonalProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return Response(UserSerializer(request.user).data)


# ---------------------------------------------------------------------------
# Perfil de prestador (BE-05)
# ---------------------------------------------------------------------------

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def provider_profile_view(request):
    """GET/PATCH del perfil propio del prestador.

    BE-04: solo el propietario puede editar; un cliente no puede.
    BE-05: validar nombre visible, experiencia, categorías, comunas.
    """
    if request.user.role != User.Role.PROVIDER:
        return Response(
            {'code': 'forbidden', 'detail': 'Solo los prestadores tienen perfil de prestador.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        profile = request.user.provider_profile
    except User.provider_profile.RelatedObjectDoesNotExist:
        return Response(
            {'code': 'not_found', 'detail': 'Perfil no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        return Response(ProviderProfileReadSerializer(profile).data)

    # PATCH — edición exclusiva del propietario (BE-05)
    serializer = ProviderProfileWriteSerializer(
        profile, data=request.data, partial=True,
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    logger.info(
        'Perfil de prestador #%d actualizado por usuario #%d',
        profile.pk, request.user.id,
    )

    return Response(ProviderProfileReadSerializer(profile).data)
