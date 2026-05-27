from django.urls import path
from .views import ETRunView

urlpatterns = [
    path('run/', ETRunView.as_view(), name='etl-run'),
]

