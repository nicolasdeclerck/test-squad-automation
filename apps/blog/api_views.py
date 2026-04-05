from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Comment, Post
from .serializers import (
    CommentSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
)


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostListCreateAPIView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateUpdateSerializer
        return PostListSerializer

    def get_queryset(self):
        return (
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .select_related("author__profile")
            .order_by("-created_at")
        )

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        post = serializer.instance
        detail_serializer = PostDetailSerializer(
            post, context={"request": request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "slug"
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def get_queryset(self):
        return (
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .select_related("author__profile")
            .prefetch_related("comments__author__profile")
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        detail_serializer = PostDetailSerializer(
            instance, context={"request": request}
        )
        return Response(detail_serializer.data)


class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = generics.get_object_or_404(
            Post,
            slug=self.kwargs["slug"],
            status=Post.STATUS_PUBLISHED,
        )
        serializer.save(author=self.request.user, post=post)


class CommentDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)
