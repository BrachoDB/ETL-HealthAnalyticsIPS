from django.urls import path
from .views import KPIView, PatientExportView

urlpatterns = [
    path('kpis/', KPIView.as_view(), name='kpis'),
    path('export/<str:export_format>/', PatientExportView.as_view(), name='patient-export'),
]
