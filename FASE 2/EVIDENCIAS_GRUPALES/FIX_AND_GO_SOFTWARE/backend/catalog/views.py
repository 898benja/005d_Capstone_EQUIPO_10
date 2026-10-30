"""Vistas de la app catalog.

Cubre BE-06 (catálogo y búsqueda de prestadores), BE-12 (filtros y paginación).
"""

from django.db import models
from django.db.models import Avg, Count

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import ProviderProfile
from core.pagination import paginate_queryset
from .models import Category, Commune
from .geo import NearbyQuery, nearby
from .serializers import (
    CategorySerializer,
    CommuneSerializer,
    ProviderDetailSerializer,
    ProviderListSerializer,
)


@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    """Lista de categorías de servicio.

    BE-06: solo categorías activas (todas por ahora; el modelo no tiene `is_active`,
    pero el orden es estable por `name`).
    BE-12: paginación aplicada.
    """
    categories = Category.objects.all()
    return paginate_queryset(request, categories, CategorySerializer)


@api_view(['GET'])
@permission_classes([AllowAny])
def commune_list(request):
    """Lista de comunas disponibles.

    BE-06: orden estable por nombre.
    BE-12: paginación aplicada.
    """
    communes = Commune.objects.all()
    return paginate_queryset(request, communes, CommuneSerializer)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_list(request):
    """Buscar prestadores activos.

    Filtros (BE-06, BE-12):
    - ?category=slug     — filtrar por categoría
    - ?commune=slug      — filtrar por comuna
    - ?search=texto      — búsqueda por nombre visible o descripción
    - ?ordering=field    — ordenar por campo (display_name, years_experience)

    BE-06: solo devuelve perfiles activos; no expone datos privados innecesarios.
    BE-12: orden estable por defecto (display_name), paginación aplicada.
    """
    qs = ProviderProfile.objects.filter(
        is_active=True, user__is_active=True,
    ).select_related('user').prefetch_related('categories', 'communes')

    # Filtro por categoría (slug)
    category_slug = request.query_params.get('category')
    if category_slug:
        qs = qs.filter(categories__slug=category_slug)

    # Filtro por comuna (slug)
    commune_slug = request.query_params.get('commune')
    if commune_slug:
        qs = qs.filter(communes__slug=commune_slug)

    # Búsqueda por texto libre (nombre visible o descripción)
    search = request.query_params.get('search')
    if search:
        qs = qs.filter(
            models.Q(display_name__icontains=search)
            | models.Q(description__icontains=search)
        )

    # BE-06: respuesta vacía (no error) cuando no hay resultados
    # BE-12: orden estable por defecto
    ordering = request.query_params.get('ordering', 'display_name')
    allowed_orderings = {
        'display_name', '-display_name',
        'years_experience', '-years_experience',
    }
    if ordering not in allowed_orderings:
        ordering = 'display_name'
    qs = qs.order_by(ordering, 'pk')

    qs = qs.distinct()

    # Anotar promedio de valoración y cantidad de servicios completados
    qs = qs.annotate(
        rating_count=Count('user__provider_requests__rating', distinct=True),
        avg_rating=Avg(
            'user__provider_requests__rating__score',
        ),
        completed_services=Count(
            'user__provider_requests',
            filter=models.Q(user__provider_requests__status='COMPLETED'),
        ),
    )

    if any(k in request.query_params for k in ('latitude', 'longitude', 'radius_km')):
        query = NearbyQuery(data=request.query_params)
        query.is_valid(raise_exception=True)
        qs = nearby(qs, query.validated_data)
    return paginate_queryset(request, qs, ProviderListSerializer)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_detail(request, pk):
    """Detalle de un prestador.

    BE-06: solo perfiles activos; el detalle público no expone datos privados.
    """
    try:
        profile = ProviderProfile.objects.select_related('user').prefetch_related(
            'categories', 'communes',
        ).annotate(avg_rating=Avg('user__provider_requests__rating__score'),rating_count=Count('user__provider_requests__rating',distinct=True)).get(pk=pk, is_active=True, user__is_active=True)
    except ProviderProfile.DoesNotExist:
        return Response(
            {'code': 'not_found', 'detail': 'Prestador no encontrado.'},
            status=404,
        )
    return Response(ProviderDetailSerializer(profile).data)
