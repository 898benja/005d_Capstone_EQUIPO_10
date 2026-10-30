"""URLs de la app services.

Incluye endpoints para solicitudes, cotizaciones, cierre (P2) y valoraciones (P2).
"""

from django.urls import path

from . import views
from .dashboard import provider_dashboard
from .evidence import evidence, evidence_photo

urlpatterns = [
    path('requests/<int:pk>/evidence/', evidence, name='work-evidence'),
    path('requests/<int:pk>/evidence/<int:evidence_id>/', evidence_photo, name='work-evidence-photo'),
    path('provider/dashboard/', provider_dashboard, name='provider-dashboard'),
    # ----- Solicitudes (BE-07, BE-08) -----
    path('requests/', views.request_list_create, name='request-list-create'),
    path('requests/<int:pk>/', views.request_detail, name='request-detail'),
    path('requests/<int:pk>/cancel/', views.request_cancel, name='request-cancel'),

    # ----- Cotizaciones (BE-09) -----
    path('requests/<int:pk>/quote/', views.quote_create_or_get, name='quote-create-or-get'),
    path('requests/<int:pk>/quote/accept/', views.quote_accept, name='quote-accept'),
    path('requests/<int:pk>/quote/reject/', views.quote_reject, name='quote-reject'),
    path('requests/<int:pk>/quote/withdraw/', views.quote_withdraw, name='quote-withdraw'),

    # ----- Cierre de servicio (P2 — BE-17) -----
    path('requests/<int:pk>/start/', views.request_start, name='request-start'),
    path('requests/<int:pk>/complete/', views.request_complete, name='request-complete'),

    # ----- Valoraciones (P2 — BE-18) -----
    path('requests/<int:pk>/rating/', views.request_rating, name='request-rating'),
]
