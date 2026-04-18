from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Comment, Post, PostImage, PostVersion, PostVideo, Tag

User = get_user_model()


class AuthorSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ("id", "username", "first_name", "last_name", "avatar")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
        read_only_fields = ("id", "slug")


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
    tags = TagSerializer(many=True, read_only=True)
    plain_content = serializers.SerializerMethodField()
    reading_time_minutes = serializers.SerializerMethodField()
    has_draft = serializers.SerializerMethodField()
    cover_image = serializers.ImageField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "author",
            "status",
            "tags",
            "cover_image",
            "plain_content",
            "reading_time_minutes",
            "has_draft",
            "is_pinned",
            "pinned_at",
            "published_at",
            "created_at",
        )
        read_only_fields = ("is_pinned", "pinned_at")

    def get_reading_time_minutes(self, obj):
        """Estime le temps de lecture (en minutes) affiché sur la liste."""
        text = obj.content or ""
        word_count = len(text.split())
        if word_count == 0:
            return 1
        # On ajuste la vitesse selon la densité (caractères par mot)
        # pour les contenus techniques avec des mots longs.
        avg_word_length = len(text) / word_count
        wpm = 200 if avg_word_length < 7 else 150
        return max(1, round(word_count / wpm))

    def get_has_draft(self, obj):
        request = self.context.get("request")
        if (
            request
            and request.user.is_authenticated
            and obj.author_id == request.user.id
        ):
            return obj.has_draft
        return False

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
    tags = TagSerializer(many=True, read_only=True)
    is_owner = serializers.SerializerMethodField()
    approved_comments = serializers.SerializerMethodField()
    has_draft = serializers.SerializerMethodField()
    draft_title = serializers.SerializerMethodField()
    draft_content = serializers.SerializerMethodField()
    cover_image = serializers.ImageField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "author",
            "content",
            "status",
            "tags",
            "cover_image",
            "is_owner",
            "approved_comments",
            "has_draft",
            "draft_title",
            "draft_content",
            "is_pinned",
            "pinned_at",
            "published_at",
            "created_at",
        )
        read_only_fields = ("is_pinned", "pinned_at")

    def _is_author(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.author_id == request.user.id
        )

    def get_is_owner(self, obj):
        return self._is_author(obj)

    def get_has_draft(self, obj):
        if self._is_author(obj):
            return obj.has_draft
        return False

    def get_draft_title(self, obj):
        if self._is_author(obj):
            return obj.draft_title
        return ""

    def get_draft_content(self, obj):
        if self._is_author(obj):
            return obj.draft_content
        return ""

    def get_approved_comments(self, obj):
        comments = (
            obj.comments.filter(is_approved=True)
            .select_related("author__profile")
            .order_by("-created_at")
        )
        return CommentSerializer(comments, many=True, context=self.context).data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
    )

    class Meta:
        model = Post
        fields = ("title", "content", "tags")

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le titre est obligatoire.")
        return value.strip()


class PostVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVersion
        fields = ("version_number", "title", "content", "published_at")
        read_only_fields = fields


class PostAutoSaveSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
    )

    class Meta:
        model = Post
        fields = ("draft_title", "draft_content", "tags")


class PostImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "image")
        read_only_fields = ("id",)


class PostVideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ("id", "video")
        read_only_fields = ("id",)
