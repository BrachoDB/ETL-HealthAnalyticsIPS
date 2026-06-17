from django.urls import path
from .views import DashboardExtrasView, ExportAuditListView, KPIView, PatientExportView

urlpatterns = [
    path('kpis/', KPIView.as_view(), name='kpis'),
    path('dashboard-extras/', DashboardExtrasView.as_view(), name='dashboard-extras'),
    path('export-audit/', ExportAuditListView.as_view(), name='export-audit'),
    path('export/<str:export_format>/', PatientExportView.as_view(), name='patient-export'),
]
