from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie


@never_cache
@ensure_csrf_cookie
def login_view(request):
    return render(request, 'login.html')


@never_cache
@login_required(login_url='/login/')
@ensure_csrf_cookie
def dashboard_view(request):
    return render(request, 'dashboard.html')
