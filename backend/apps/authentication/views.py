from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, RegisterSerializer
from .models import User


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny if settings.OPEN_REGISTRATION else permissions.IsAdminUser,)
    serializer_class = RegisterSerializer


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


@require_POST
@csrf_exempt
@ensure_csrf_cookie
def session_login_view(request):
    payload = request.POST.dict()
    if not payload and request.content_type == 'application/json':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            payload = {}

    username = payload.get('username')
    password = payload.get('password')
    remember = str(payload.get('remember', '')).lower() in ('1', 'true', 'on', 'yes')
    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Credenciales inválidas'}, status=401)

    login(request, user)

    # "Recordarme": si está marcado, la sesión persiste según SESSION_COOKIE_AGE
    # (valor por defecto de Django). Si no, expira al cerrar el navegador.
    request.session.set_expiry(None if remember else 0)

    return JsonResponse({'status': 'ok'})
