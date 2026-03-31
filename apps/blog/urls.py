from django.urls import path

from .views import HomeView, PostCreateView, PostListView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("articles/", PostListView.as_view(), name="post_list"),
    path("articles/creer/", PostCreateView.as_view(), name="post_create"),
]
