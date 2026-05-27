from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='dashboard/dashboard.html'), name='root-dashboard'),
    path('login/', TemplateView.as_view(template_name='dashboard/login.html'), name='frontend-login'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard/dashboard.html'), name='frontend-dashboard'),
]


