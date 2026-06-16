from django.urls import path

from .views import ReportsExportView

urlpatterns = [
    path('export/<str:export_format>/', ReportsExportView.as_view(), name='reports-export'),
]


