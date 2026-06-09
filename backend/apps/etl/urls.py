from django.urls import path
from .views import ETLRunView, PacientesView, ETLHistoryView

urlpatterns = [
    path('etl/run/', ETLRunView.as_view(), name='etl-run'),
    path('etl/history/', ETLHistoryView.as_view(), name='etl-history'),
    path('pacientes/', PacientesView.as_view(), name='pacientes'),
]





