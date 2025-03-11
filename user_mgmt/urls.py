from django.urls import path
from . import views

urlpatterns = [
    path("auth/login/steam", views.steam_login, name="steam_login"),
    path("auth/steam/callback", views.steam_callback, name="steam_callback"),
    path('user-auth/', views.userAuth, name='user_auth'),
    path('user-info/', views.getUserInfo, name='user_info'),
    path('player-favorites/<int:player_id>/', views.favorites_player, name='favorite_player'),
    path('match-favorites/<int:match_id>/', views.favorites_match, name='favorite_match'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('logout/', views.logout_view, name='logout')
]