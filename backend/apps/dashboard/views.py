from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def login_view(request):
    return render(request, 'login.html')


@ensure_csrf_cookie
def dashboard_view(request):
    return render(request, 'dashboard.html')
