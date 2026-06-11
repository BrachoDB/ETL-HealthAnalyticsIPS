from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ETLLogViewSet

router = DefaultRouter()
router.register('data', PatientViewSet)
router.register('logs', ETLLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
