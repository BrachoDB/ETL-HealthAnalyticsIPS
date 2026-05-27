from django.urls import path

from .views import (
    KPIsView,
    SegmentacionView,
    PieRiesgoView,
    SeriesTendenciasView,
    HeatmapView,
)

urlpatterns = [
    path('kpis/', KPIsView.as_view(), name='dashboard-kpis'),
    path('segmentacion/', SegmentacionView.as_view(), name='dashboard-segmentacion'),
    path('pie-riesgo/', PieRiesgoView.as_view(), name='dashboard-pie-riesgo'),
    path('series-tendencias/', SeriesTendenciasView.as_view(), name='dashboard-series-tendencias'),
    path('heatmap/', HeatmapView.as_view(), name='dashboard-heatmap'),
]


