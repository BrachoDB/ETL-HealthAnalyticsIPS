from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
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


@never_cache
@login_required(login_url='/login/')
@ensure_csrf_cookie
def etl_view(request):
    return render(request, 'etl.html')


@never_cache
@login_required(login_url='/login/')
@ensure_csrf_cookie
def analytics_view(request):
    return render(request, 'analytics.html')


@never_cache
@login_required(login_url='/login/')
@ensure_csrf_cookie
def ml_view(request):
    return render(request, 'ml.html')


@never_cache
@login_required(login_url='/login/')
@ensure_csrf_cookie
def pacientes_view(request):
    return render(request, 'pacientes.html')


@never_cache
@login_required(login_url='/login/')
@ensure_csrf_cookie
def reportes_view(request):
    return render(request, 'reportes.html')


@never_cache
@login_required(login_url='/login/')
@ensure_csrf_cookie
def profile_view(request):
    user = request.user
    context = {}

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        errors = []
        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('El correo electrónico no es válido.')

        if errors:
            context['errors'] = errors
            # Conservamos lo que el usuario escribió para no perderlo.
            context['form_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
            }
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save(update_fields=['first_name', 'last_name', 'email'])
            context['success'] = 'Perfil actualizado correctamente.'

    return render(request, 'perfil.html', context)


@never_cache
@login_required(login_url='/login/')
@ensure_csrf_cookie
def settings_view(request):
    context = {}

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Evita que el usuario quede deslogueado tras cambiar la contraseña.
            update_session_auth_hash(request, user)
            context['success'] = 'Contraseña actualizada correctamente.'
            form = PasswordChangeForm(request.user)
        context['form'] = form
    else:
        context['form'] = PasswordChangeForm(request.user)

    return render(request, 'configuracion.html', context)
