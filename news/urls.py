from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_index, name='news_index'),
    path('videos/', views.video_index, name='video_index'),
    path('category/<slug:category_slug>/', views.category_view, name='category_view'),
    path('topic/<slug:topic_slug>/', views.topic_view, name='topic_view'),
    path('author/<slug:author_slug>/', views.author_view, name='author_view'),
    path('archive/', views.archive_view, name='archive'),
    path('search/', views.search_view, name='search'),
    path('breaking/', views.breaking_news_view, name='breaking_news'),
    path('trending/', views.trending_news_view, name='trending_news'),
]
