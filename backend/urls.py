from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

# Define the schema view with OpenAPI 3.0 information
schema_view = get_schema_view(
    openapi.Info(
        title="Chat API",
        default_version='v1',
        description="API documentation for the chat application.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@chat.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(SessionAuthentication, TokenAuthentication),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("chat.urls")),  # Your non-API URLs
    path("api/v1/", include("chat.api.urls")),  # Your API URLs

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),

    # Redoc UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),

    # OpenAPI 3.0 JSON and YAML schema
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]
