from django.urls import path
from .views import BatchPredictionAPIView, PredictionAPIView

urlpatterns = [
    path('predict/', PredictionAPIView.as_view(), name='predict'),
    path('predict/batch/', BatchPredictionAPIView.as_view(), name='predict-batch'),
]
