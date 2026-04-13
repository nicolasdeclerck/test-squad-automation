from django.urls import path

from .api_views import (
    CommentCreateAPIView,
    CommentDeleteAPIView,
    PostAutoSaveView,
    PostDetailAPIView,
    PostImageUploadView,
    PostListCreateAPIView,
    PostPublishView,
    PostVersionDetailAPIView,
    PostVersionListAPIView,
    PostVersionRestoreAPIView,
    PostVideoUploadView,
    TagListAPIView,
)

urlpatterns = [
    path("tags/", TagListAPIView.as_view(), name="api_tag_list"),
    path(
        "upload-image/",
        PostImageUploadView.as_view(),
        name="api_post_image_upload",
    ),
    path(
        "upload-video/",
        PostVideoUploadView.as_view(),
        name="api_post_video_upload",
    ),
    path("posts/", PostListCreateAPIView.as_view(), name="api_post_list"),
    path(
        "posts/<slug:slug>/",
        PostDetailAPIView.as_view(),
        name="api_post_detail",
    ),
    path(
        "posts/<slug:slug>/autosave/",
        PostAutoSaveView.as_view(),
        name="api_post_autosave",
    ),
    path(
        "posts/<slug:slug>/publish/",
        PostPublishView.as_view(),
        name="api_post_publish",
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
    path(
        "posts/<slug:slug>/versions/",
        PostVersionListAPIView.as_view(),
        name="api_post_versions",
    ),
    path(
        "posts/<slug:slug>/versions/<int:version_number>/",
        PostVersionDetailAPIView.as_view(),
        name="api_post_version_detail",
    ),
    path(
        "posts/<slug:slug>/versions/<int:version_number>/restore/",
        PostVersionRestoreAPIView.as_view(),
        name="api_post_version_restore",
    ),
]
