from django.urls import path

from .views import (
    CommentCreateView,
    CommentDeleteView,
    HomeView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostListView,
    PostUpdateView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("articles/", PostListView.as_view(), name="post_list"),
    path("articles/creer/", PostCreateView.as_view(), name="post_create"),
    path(
        "articles/<slug:slug>/modifier/",
        PostUpdateView.as_view(),
        name="post_update",
    ),
    path(
        "articles/<slug:slug>/supprimer/",
        PostDeleteView.as_view(),
        name="post_delete",
    ),
    path(
        "articles/<slug:slug>/",
        PostDetailView.as_view(),
        name="post_detail",
    ),
    path(
        "articles/<slug:slug>/commenter/",
        CommentCreateView.as_view(),
        name="comment_create",
    ),
    path(
        "articles/<slug:slug>/commentaire/<int:pk>/supprimer/",
        CommentDeleteView.as_view(),
        name="comment_delete",
    ),
]
