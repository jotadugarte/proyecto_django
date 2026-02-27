from django.urls import path, include
from . import views

urlpatterns = [
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.CustomLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("planet/<int:planet_id>/", views.planet_detail, name="planet_detail"),
    path("", views.index, name="index"),
    
    # Game Master Dashboard Routes
    path("game-master/", views.gm_dashboard, name="gm_dashboard"),
    path("game-master/settings/", views.gm_edit_settings, name="gm_edit_settings"),
    path("game-master/building/<int:pk>/", views.gm_edit_building, name="gm_edit_building"),
    path("game-master/unit/<int:pk>/", views.gm_edit_unit, name="gm_edit_unit"),
]
