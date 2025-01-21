from django.urls import path
from . import views

urlpatterns = [
    path('<int:dl_match_id>/', views.match_detail, name='match_detail'),
    path('<int:dl_match_id>/create/', views.create_match_from_metadata, name='create_match_from_metadata'),
]
