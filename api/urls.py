from django.urls import path, include
from .views import anime_search
from django.contrib.auth import views as auth_views
urlpatterns =  [

    path('search/',anime_search),
]
