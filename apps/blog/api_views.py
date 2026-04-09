from django.db import IntegrityError
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Comment, Post, PostVersion, Tag
from .serializers import (
    CommentSerializer,
    PostAutoSaveSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostImageUploadSerializer,
    PostListSerializer,
    PostVersionSerializer,
    TagSerializer,
)


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


def _set_tags(post, tag_names):
    """Get or create tags by name and set them on the post."""
    if tag_names is None:
        return
    tags = []
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
        try:
            tag, _ = Tag.objects.get_or_create(
                name__iexact=name,
                defaults={"name": name},
            )
        except IntegrityError:
            tag = Tag.objects.get(name__iexact=name)
        tags.append(tag)
    current_ids = set(post.tags.values_list("id", flat=True))
    new_ids = {t.id for t in tags}
    if current_ids != new_ids:
        post.tags.set(tags)


class TagListAPIView(generics.ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Tag.objects.all()
        search = self.request.query_params.get("search", "").strip()
        if search:
            return qs.filter(name__icontains=search)[:5]
        return qs[:20]


class PostListCreateAPIView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateUpdateSerializer
        return PostListSerializer

    def get_queryset(self):
        qs = (
            Post.objects.select_related("author__profile")
            .prefetch_related("tags")
            .order_by("-created_at")
        )
        status_filter = self.request.query_params.get("status")
        if (
            status_filter == "draft"
            and self.request.user.is_authenticated
            and self.request.user.is_superuser
        ):
            return qs.filter(
                status=Post.STATUS_DRAFT, author=self.request.user
            )
        return qs.filter(status=Post.STATUS_PUBLISHED)

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsSuperUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        tag_names = serializer.validated_data.pop("tags", [])
        serializer.save(
            author=self.request.user,
            status=Post.STATUS_DRAFT,
            draft_title=serializer.validated_data.get("title", ""),
            draft_content=serializer.validated_data.get("content", ""),
            has_draft=True,
        )
        _set_tags(serializer.instance, tag_names)

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

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsSuperUser(), IsAuthorOrReadOnly()]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def get_queryset(self):
        qs = (
            Post.objects.select_related("author__profile")
            .prefetch_related("comments__author__profile", "tags")
        )
        if self.request.user.is_authenticated:
            return qs.filter(
                Q(status=Post.STATUS_PUBLISHED) | Q(author=self.request.user)
            )
        return qs.filter(status=Post.STATUS_PUBLISHED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if instance.status == Post.STATUS_PUBLISHED:
            return Response(
                {
                    "error": "Un article publié ne peut pas être modifié directement. "
                    "Utilisez l'endpoint autosave pour éditer le brouillon."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        tag_names = serializer.validated_data.pop("tags", None)
        self.perform_update(serializer)
        _set_tags(instance, tag_names)
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


class PostAutoSaveView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def patch(self, request, slug):
        post = generics.get_object_or_404(
            Post, slug=slug, author=request.user
        )
        serializer = PostAutoSaveSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        tag_names = serializer.validated_data.pop("tags", None)
        serializer.save(has_draft=True)
        _set_tags(post, tag_names)
        return Response({"status": "saved"})


class PostPublishView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def post(self, request, slug):
        post = generics.get_object_or_404(
            Post, slug=slug, author=request.user
        )
        if not (post.draft_title or "").strip() and not (post.title or "").strip():
            return Response(
                {"error": "Le titre est requis pour publier."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        post.publish()
        detail_serializer = PostDetailSerializer(
            post, context={"request": request}
        )
        return Response(detail_serializer.data)


class CommentDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)


class PostVersionListAPIView(generics.ListAPIView):
    serializer_class = PostVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post = generics.get_object_or_404(
            Post, slug=self.kwargs["slug"]
        )
        if post.author != self.request.user:
            self.permission_denied(self.request)
        return PostVersion.objects.filter(post=post)


class PostVersionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PostVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "version_number"

    def get_queryset(self):
        post = generics.get_object_or_404(
            Post, slug=self.kwargs["slug"]
        )
        if post.author != self.request.user:
            self.permission_denied(self.request)
        return PostVersion.objects.filter(post=post)


class PostImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "uploads"

    def post(self, request):
        serializer = PostImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(uploaded_by=request.user)
        return Response(
            {"url": serializer.instance.image.url},
            status=status.HTTP_201_CREATED,
        )


class PostVersionRestoreAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def post(self, request, slug, version_number):
        post = generics.get_object_or_404(Post, slug=slug)
        if post.author != request.user:
            self.permission_denied(request)
        version = generics.get_object_or_404(
            PostVersion, post=post, version_number=version_number
        )
        post.draft_title = version.title
        post.draft_content = version.content
        post.has_draft = True
        post.save()
        return Response(
            {"status": "restored", "version_number": version.version_number}
        )
