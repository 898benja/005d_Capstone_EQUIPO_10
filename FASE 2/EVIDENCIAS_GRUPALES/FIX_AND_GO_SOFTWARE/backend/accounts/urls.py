from django.urls import path

from . import views
from .avatar import avatar

urlpatterns = [
    path('me/provider-profile/avatar/', avatar, name='provider-avatar'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.me_view, name='me'),
    path('me/provider-profile/', views.provider_profile_view, name='provider-profile'),
]
