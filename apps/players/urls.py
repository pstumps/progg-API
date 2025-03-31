from django.urls import path
from . import views

urlpatterns = [
    # Test stats for testing only
    path('<int:steam_id3>', views.stats, name='stats'),
    # path('<int:steam_id3>', views.testStats, name='stats'),
    path('<int:steam_id3>/heroes/', views.playerHeroes, name='playerHeroes'),
    path('<int:steam_id3>/match-history/', views.matchHistory, name='matchHistory'),
    path('<int:steam_id3>/top-player-heroes', views.topPlayerHeroes, name='topPlayerHeroes'),
    path('<int:steam_id3>/match-history-data', views.getMatchHistoryData, name='matchHistoryData'),
    path('<int:steam_id3>/steam-info', views.getSteamInfo, name='getSteamInfo'),
    path('<int:steam_id3>/update-steam-info', views.updatePlayerSteamWebAPI, name='updatePlayerSteamWebAPI'),
    path('<int:steam_id3>/deadlock-api-match-history', views.getDeadlockAPIMatchHistory, name='getDeadlockAPIMatchHistory'),
    path('<int:steam_id3>/search-item/', views.search_history_player_item, name='searchHistoryMatchItem'),
    path('<int:steam_id3>/calculate-rank', views.calculateRank, name='calculateRank'),
    path('<int:steam_id3>/records', views.playerRecords, name='playerRecords'),
    path('delete-all-data', views.deleteAllData, name='deleteAllData')
]