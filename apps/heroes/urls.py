from django.urls import path
from . import views

urlpatterns = [
    path('update-stats/', views.updateStats, name='updateStats'),
    path('data/', views.data, name='data')
]