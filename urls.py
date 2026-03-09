from django.contrib import admin
from django.urls import path
from anime.views import anime_search

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/anime-search/', anime_search, name='anime_search'),
]
