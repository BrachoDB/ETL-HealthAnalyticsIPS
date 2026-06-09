from django.urls import path
from .views import KPIsView
from django.views.generic import TemplateView

urlpatterns = [
    path('dashboard/kpis/', KPIsView.as_view(), name='dashboard-kpis'),
    path('', TemplateView.as_view(template_name='dashboard_spa.html'), name='dashboard-spa'),
]



