from django.urls import path
from . import views

urlpatterns = [
    path('planet/<int:planet_id>/', views.planet_detail, name='planet_detail'),
    path('', views.index, name='index'), # Redirect to main planet
]
