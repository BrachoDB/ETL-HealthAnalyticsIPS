from django.urls import path
from .views import ETLRunView, PacientesView

urlpatterns = [
    path('etl/run/', ETLRunView.as_view(), name='etl-run'),
    path('pacientes/', PacientesView.as_view(), name='pacientes'),
]


