from django.urls import path
from .views import DashboardExtrasView, KPIView, PatientExportView

urlpatterns = [
    path('kpis/', KPIView.as_view(), name='kpis'),
    path('dashboard-extras/', DashboardExtrasView.as_view(), name='dashboard-extras'),
    path('export/<str:export_format>/', PatientExportView.as_view(), name='patient-export'),
]
