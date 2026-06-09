from django.urls import path

from .views import PredictView, PredictionsView, TrainView

urlpatterns = [
    # Compatibilidad con stubs previos
    path('ml/train/', TrainView.as_view(), name='ml-train'),
    path('ml/predict/', PredictView.as_view(), name='ml-predict'),

    # API requerida
    path('predicciones/', PredictionsView.as_view(), name='predicciones'),
]

