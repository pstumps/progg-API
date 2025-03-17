from django.urls import path
from . import views

urlpatterns = [
    path('<int:dl_match_id>/', views.match_details, name='match_detail'),
    path('<int:dl_match_id>/<int:user_id>', views.match_details, name='user_match_details'),
    #path('<int:dl_match_id>/create/', views.create_match_from_metadata, name='create_match_from_metadata'),
    path('<int:dl_match_id>/graphs/', views.graphs, name='graphs'),
    path('<int:dl_match_id>/damage-graphs/', views.damageGraphs, name='damageGraphs'),
    path('<int:dl_match_id>/timeline/', views.timelines, name='match_timeline'),
    path('<int:dl_match_id>/timeline/<int:user_id>', views.timelines, name='match_timeline'),
    path('<int:dl_match_id>/user-details/', views.user_match_details, name='user_match_details'),
    path('<int:dl_match_id>/search-item/', views.search_history_match_item, name='searchHistoryMatchItem'),
    path('items/', views.getItemsDict, name='getItemsDict'),
]
