"""Resumen privado del prestador: nunca publica un directorio de domicilios."""
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from accounts.permissions import IsProvider
from .models import ServiceRequest


@api_view(['GET'])
@permission_classes([IsProvider])
def provider_dashboard(request):
    jobs = ServiceRequest.objects.filter(provider=request.user)
    counts = dict(jobs.values_list('status').annotate(total=Count('id')))
    # Límites explícitos mantienen liviano el inicio; Solicitudes conserva el historial paginado.
    recent = list(jobs.select_related('client', 'category', 'commune')[:20])
    customers = jobs.filter(status='COMPLETED').values(
        'client_id', 'client__first_name', 'client__last_name',
    ).annotate(jobs=Count('id')).order_by('-jobs', 'client_id')[:20]
    return Response({
        'warning_count': request.user.service_warnings.count(),
        'counts': counts,
        'recent': [{
            'id': job.id, 'client_name': job.client.get_full_name() or 'Cliente',
            'category_name': job.category.name, 'commune_name': job.commune.name,
            'status': job.status, 'status_display': job.get_status_display(),
            'latitude': job.latitude, 'longitude': job.longitude,
        } for job in recent],
        'customers': [{
            'id': row['client_id'],
            'name': f"{row['client__first_name']} {row['client__last_name']}".strip() or 'Cliente',
            'completed_jobs': row['jobs'],
        } for row in customers],
    })
