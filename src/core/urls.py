from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication

class SwaggerSchemaPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        path = request.path
        if path.startswith('/swagger/') or path.startswith('/redoc/'):
            return True
        return super().has_permission(request, view)

schema_view = get_schema_view(
    openapi.Info(
        title="RSS feeds APIs",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(), 
)

urlpatterns = [
    path('feeds/', include([
        path('admin/', admin.site.urls),
        path('api/', include([
            path('rss/', include('rss_channels.urls')),
            path('articles/', include('articles.urls')),
        ])),

        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ])),

]
