from django.urls import path
from . import views

urlpatterns = [
    path('user-auth/', views.userAuth, name='user_auth'),
]