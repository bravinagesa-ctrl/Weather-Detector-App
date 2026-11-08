from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('weather-data/', views.weather_data, name='weather_data'),
]