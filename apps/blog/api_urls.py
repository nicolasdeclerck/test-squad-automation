from django.urls import path

from .api_views import (
    CommentCreateAPIView,
    CommentDeleteAPIView,
    PostDetailAPIView,
    PostListCreateAPIView,
)

urlpatterns = [
    path("posts/", PostListCreateAPIView.as_view(), name="api_post_list"),
    path(
        "posts/<slug:slug>/",
        PostDetailAPIView.as_view(),
        name="api_post_detail",
    ),
    path(
        "posts/<slug:slug>/comments/",
        CommentCreateAPIView.as_view(),
        name="api_comment_create",
    ),
    path(
        "comments/<int:pk>/",
        CommentDeleteAPIView.as_view(),
        name="api_comment_delete",
    ),
]
