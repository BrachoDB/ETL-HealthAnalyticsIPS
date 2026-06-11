from django.urls import path
from .views import KPIView

urlpatterns = [
    path('kpis/', KPIView.as_view(), name='kpis'),
]
