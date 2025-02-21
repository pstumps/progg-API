from django.urls import path
from . import views

urlpatterns = [
    path("auth/login/steam", views.steam_login, name="steam_login"),
    path("auth/steam/callback", views.steam_callback, name="steam_callback"),
    path('user-auth/', views.userAuth, name='user_auth'),
    path('user-info/', views.getUserInfo, name='user_info'),
]