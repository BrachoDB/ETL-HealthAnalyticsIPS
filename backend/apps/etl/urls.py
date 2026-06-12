from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ETLLogViewSet, PatientViewSet, UploadCSVView

router = DefaultRouter()
router.register('data', PatientViewSet)
router.register('logs', ETLLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload-csv/', UploadCSVView.as_view(), name='upload-csv'),
]
