from django.urls import path
from . import views

urlpatterns = [
    path('<int:steam_id3>', views.stats, name='stats'),
    path('<int:steam_id3>/match-history/', views.matchHistory, name='matchHistory'),
    path('<int:steam_id3>/top-player-heroes', views.topPlayerHeroes, name='topPlayerHeroes'),
    path('<int:steam_id3>/match-history-data', views.getMatchHistoryData, name='matchHistoryData'),
    path('<int:steam_id3>/steam-info', views.getSteamInfo, name='getSteamInfo'),
    path('<int:steam_id3>/update-steam-info', views.updatePlayerSteamWebAPI, name='updatePlayerSteamWebAPI'),
    path('delete-all-data', views.deleteAllData, name='deleteAllData')
]