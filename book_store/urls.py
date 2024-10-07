from django.urls import path, include
from drf_spectacular.views import SpectacularRedocView
from django.contrib import admin
from .swagger_views import CustomSchemaView, CustomSpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),
    path('users/', include('users.urls')),
    path('api/schema/', CustomSchemaView.as_view(api_version='v2'), name='schema'),
    path('api/schema/swagger-ui/', CustomSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/auth/', include('authentication.urls')),
]