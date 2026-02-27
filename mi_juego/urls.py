"""
URL configuration for mi_juego project.
All app-level routes are delegated to core.urls.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
