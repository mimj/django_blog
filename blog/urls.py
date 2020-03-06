from django.urls import path

from blog.feeds import LatestPostsFeed
from blog.views import post_list, PostDetail, post_detail, post_share, search, redisearch, redirect_to_post_detail

app_name = 'blog'

urlpatterns = [
    path('<int:year>/<int:month>/<int:day>/<slug:post_slug>/', post_detail, name='post_detail'),
    path('post/<int:post_id>/', redirect_to_post_detail, name='redirect_to_post_detail'),
    path('', post_list, name='post_list'),
    path('search/', search, name='search'),
    path('redisearch/', redisearch, name='redisearch'),
    path('tag/<slug:tag_slug>/', post_list, name='post_list_by_tag'),
    path('<int:post_id>/share/', post_share, name='post_share'),
    path('feed/', LatestPostsFeed(), name='post_feed')
]
