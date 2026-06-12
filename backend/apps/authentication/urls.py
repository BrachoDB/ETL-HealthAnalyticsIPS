from django.urls import path
from .views import RegisterView, UserDetailView, session_login_view

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserDetailView.as_view(), name='me'),
    path('session-login/', session_login_view, name='session-login'),
]
