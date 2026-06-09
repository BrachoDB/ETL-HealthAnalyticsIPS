from django.urls import path
from .views import ReportsView

urlpatterns = [
    path('reportes/', ReportsView.as_view(), name='reports'),
]

