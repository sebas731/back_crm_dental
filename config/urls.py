"""
URL configuration for config project.

API montada bajo /api/. Autenticación por JWT (SimpleJWT):
  POST /api/auth/token/          -> obtener access + refresh
  POST /api/auth/token/refresh/  -> renovar access
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth (JWT)
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Apps
    path("api/", include("apps.users.urls")),
    path("api/", include("apps.pacientes.urls")),
    path("api/", include("apps.citas.urls")),
    path("api/", include("apps.ventas.urls")),
]

# Servir archivos subidos (documentos) en desarrollo.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
