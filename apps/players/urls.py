from django.urls import path
from . import views

urlpatterns = [
    path('/<int:steam_id3>/recent-matches/', views.recentMatches, name='recentMatches'),
]