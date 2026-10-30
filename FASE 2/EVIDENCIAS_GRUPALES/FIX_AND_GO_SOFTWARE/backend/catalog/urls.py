from django.urls import path

from . import views

urlpatterns = [
    path('categories/', views.category_list, name='category-list'),
    path('communes/', views.commune_list, name='commune-list'),
    path('providers/', views.provider_list, name='provider-list'),
    path('providers/<int:pk>/', views.provider_detail, name='provider-detail'),
]
