from django.urls import path

from .views import PrediccionView, PrediccionTrainView

urlpatterns = [
    path('', PrediccionView.as_view(), name='predicciones'),
    path('train/', PrediccionTrainView.as_view(), name='predicciones-train'),
]


