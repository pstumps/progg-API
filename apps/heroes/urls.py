from django.urls import path
from . import views

urlpatterns = [
    path('update-stats/', views.updateStats, name='updateStats'),
    path('data/', views.data, name='data'),
    path('data/<str:hero_name>/', views.data, name='data_by_name'),
    path('calculate-tiers/', views.calculateTier, name='calculateTier'),
    path('synergies/', views.synergies, name='synergies'),
    path('synergies/<str:hero_name>/', views.synergies, name='synergies_by_hero'),
]