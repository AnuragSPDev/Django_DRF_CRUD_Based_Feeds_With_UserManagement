from django.urls import path
from . import views

urlpatterns = [
    path('feeds_list_create/', views.FeedsListCreateView.as_view(), name='feeds_list_create'),
    path('feed_comments/', views.FeedCommentsView.as_view(), name='feed_comments'),
    path('feed_likes/', views.FeedLikeView.as_view(), name='feed_likes'),
    path('feed_detail_edit_delete/<int:pk>', 
         views.FeedRetrieveUpdateDestroyView.as_view(), name='feed_detail_edit_delete'),
]
