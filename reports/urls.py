from django.urls import path

from .views import ExportCSVView, ExportExcelView, ExportPDFView, ReportesView

urlpatterns = [
    path('', ReportesView.as_view(), name='reportes'),
    path('export/csv/', ExportCSVView.as_view(), name='export-csv'),
    path('export/excel/', ExportExcelView.as_view(), name='export-excel'),
    path('export/pdf/', ExportPDFView.as_view(), name='export-pdf'),
]


