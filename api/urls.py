from django.urls import path, include
from .views import anime_search,episode_detail,get_stream
from django.contrib.auth import views as auth_views
urlpatterns =  [

    path('search/',anime_search),
    path('list/<int:anime_id>',episode_detail),
    path('stream/<slug:episode_slug>',get_stream),

]