"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('weather/', views.weather_view, name='weather'),
    path('city_weather/', views.city_weather, name='city_weather'),
    path('add_city/', views.add_city, name='add_city'),
    path('delete_city/<int:city_id>/', views.delete_city, name='delete_city'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.myLogin, name='login'),
    path('logout/', views.myLogout, name='logout'),
]
