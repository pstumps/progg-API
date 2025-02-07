from django.urls import path
from . import views

urlpatterns = [
    path('<int:dl_match_id>/', views.match_detail, name='match_detail'),
    path('<int:dl_match_id>/create/', views.create_match_from_metadata, name='create_match_from_metadata'),
    path('<int:dl_match_id>/timeline/', views.timelines, name='match_timeline'),
    path('<int:dl_match_id>/timeline/<int:user_id>', views.timelines, name='match_timeline')
]
