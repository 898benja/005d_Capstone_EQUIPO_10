"""Paginación reutilizable para vistas funcionales (BE-12).

GenericAPIView aplica paginación automáticamente. Las vistas funcionales
(@api_view) necesitan aplicarla manualmente. Este helper estandariza la
paginación usando la configuración global de DRF.
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Paginación estándar para el MVP.

    BE-12: 20 resultados por página, configurable vía query param.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


def paginate_queryset(request, queryset, serializer_class, context=None):
    """Pagina un queryset y retorna la respuesta paginada.

    Uso en vistas funcionales:
        return paginate_queryset(request, qs, MySerializer)

    Retorna Response con formato:
    {
        "count": total,
        "next": url | null,
        "previous": url | null,
        "results": [...]
    }
    """
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = serializer_class(page, many=True, context=context or {})
        return paginator.get_paginated_response(serializer.data)
    serializer = serializer_class(queryset, many=True, context=context or {})
    from rest_framework.response import Response
    return Response(serializer.data)
