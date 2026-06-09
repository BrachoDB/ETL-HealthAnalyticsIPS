from django.urls import path

from .csv_export import CSVExportView
from .excel_export import ExcelExportView
from .pdf_export import PDFExportView
from .views import ReportsView

urlpatterns = [
    path('reportes/', ReportsView.as_view(), name='reports'),
    path('reportes/export/csv/', CSVExportView.as_view(), name='reports-export-csv'),
    path('reportes/export/excel/', ExcelExportView.as_view(), name='reports-export-excel'),
    path('reportes/export/pdf/', PDFExportView.as_view(), name='reports-export-pdf'),
]

