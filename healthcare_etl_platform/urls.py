from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI schema + docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),

    # API apps
    path('api/', include('authentication.urls')),
    path('api/', include('etl.urls')),
    path('api/', include('analytics.urls')),
    path('api/', include('ml.urls')),
    path('api/', include('dashboard.urls')),
    path('dashboard/', include('dashboard.urls')),

    path('api/', include('reports.urls')),
]

