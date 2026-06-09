from django.urls import path

from .views import AnalyticsStatsView

urlpatterns = [
    path('analytics-stats/', AnalyticsStatsView.as_view(), name='analytics-stats'),
]

