from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Comment, Post

User = get_user_model()


class AuthorSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ("id", "username", "first_name", "last_name", "avatar")


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "author",
            "is_approved",
            "is_owner",
            "created_at",
        )
        read_only_fields = ("id", "author", "is_approved", "created_at")

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False


class PostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    plain_content = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "author",
            "status",
            "plain_content",
            "published_at",
            "created_at",
        )

    def get_plain_content(self, obj):
        import json

        try:
            blocks = json.loads(obj.content)
            texts = []

            def extract_text(items):
                for item in items:
                    if isinstance(item, dict):
                        for c in item.get("content", []):
                            if isinstance(c, dict) and c.get("type") == "text":
                                texts.append(c.get("text", ""))
                        extract_text(item.get("children", []))

            extract_text(blocks)
            return " ".join(texts)[:200]
        except (json.JSONDecodeError, TypeError):
            return obj.content[:200]


class PostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()
    approved_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "author",
            "content",
            "status",
            "is_owner",
            "approved_comments",
            "has_draft",
            "draft_title",
            "draft_content",
            "published_at",
            "created_at",
        )

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False

    def get_approved_comments(self, obj):
        comments = (
            obj.comments.filter(is_approved=True)
            .select_related("author__profile")
            .order_by("-created_at")
        )
        return CommentSerializer(
            comments, many=True, context=self.context
        ).data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "content")


class PostAutoSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("draft_title", "draft_content")
