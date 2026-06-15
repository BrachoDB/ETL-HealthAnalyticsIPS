from django.urls import path
from .views import dashboard_view, login_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]
