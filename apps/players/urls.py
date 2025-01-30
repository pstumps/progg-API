from django.urls import path
from . import views

urlpatterns = [
    path('<int:steam_id3>/recent-matches/', views.recentMatches, name='recentMatches'),
    path('<int:steam_id3>', views.stats, name='stats'),
    path('<int:steam_id3>/match-history/', views.matchHistory, name='matchHistory')
]