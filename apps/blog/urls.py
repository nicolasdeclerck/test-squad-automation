from django.urls import path

from apps.blog import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("nouveau/", views.PostCreateView.as_view(), name="post_create"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path(
        "<slug:slug>/modifier/",
        views.PostUpdateView.as_view(),
        name="post_update",
    ),
]
