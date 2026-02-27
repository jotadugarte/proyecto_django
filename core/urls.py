from django.urls import path, include
from . import views

urlpatterns = [
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.CustomLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("planet/<int:planet_id>/", views.planet_detail, name="planet_detail"),
    path("", views.index, name="index"),
]
