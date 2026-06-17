from django.urls import path
from .views import (
    dashboard_view, login_view, etl_view, analytics_view,
    ml_view, pacientes_view, reportes_view, profile_view, settings_view
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('etl/', etl_view, name='etl'),
    path('analytics/', analytics_view, name='analytics'),
    path('ml/', ml_view, name='ml'),
    path('pacientes/', pacientes_view, name='pacientes'),
    path('reportes/', reportes_view, name='reportes'),
    path('perfil/', profile_view, name='perfil'),
    path('configuracion/', settings_view, name='configuracion'),
]
