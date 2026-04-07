import pytest
from django.db import IntegrityError

from apps.blog.models import Comment, Post, PostVersion

from .factories import CommentFactory, PostFactory, PostVersionFactory


@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self):
        post = PostFactory()
        assert Post.objects.filter(pk=post.pk).exists()

    def test_slug_auto_generated(self):
        post = PostFactory(title="Mon premier article")
        assert post.slug == "mon-premier-article"

    def test_slug_collision(self):
        PostFactory(title="Même titre")
        post2 = PostFactory(title="Même titre")
        assert post2.slug == "meme-titre-1"

    def test_slug_collision_multiple(self):
        PostFactory(title="Doublon")
        PostFactory(title="Doublon")
        post3 = PostFactory(title="Doublon")
        assert post3.slug == "doublon-2"

    def test_default_status_is_published(self):
        post = PostFactory()
        assert post.status == Post.STATUS_PUBLISHED

    def test_created_at_auto_set(self):
        post = PostFactory()
        assert post.created_at is not None

    def test_str_returns_title(self):
        post = PostFactory(title="Test titre")
        assert str(post) == "Test titre"


@pytest.mark.django_db
class TestCommentModel:
    def test_is_approved_false_by_default(self):
        comment = CommentFactory()
        assert comment.is_approved is False

    def test_str_representation(self):
        comment = CommentFactory()
        expected = f"Commentaire de {comment.author} sur {comment.post}"
        assert str(comment) == expected

    def test_cascade_delete_with_post(self):
        comment = CommentFactory()
        post_pk = comment.post.pk
        comment.post.delete()
        assert not Comment.objects.filter(post_id=post_pk).exists()


@pytest.mark.django_db
class TestPostVersionModel:
    def test_create_post_version(self):
        version = PostVersionFactory()
        assert PostVersion.objects.filter(pk=version.pk).exists()
        assert version.post is not None
        assert version.version_number >= 1
        assert version.title
        assert version.published_at is not None

    def test_unique_version_number_per_post(self):
        version = PostVersionFactory(version_number=1)
        with pytest.raises(IntegrityError):
            PostVersionFactory(post=version.post, version_number=1)

    def test_ordering_by_version_number_desc(self):
        post = PostFactory()
        v1 = PostVersionFactory(post=post, version_number=1)
        v2 = PostVersionFactory(post=post, version_number=2)
        v3 = PostVersionFactory(post=post, version_number=3)
        versions = list(PostVersion.objects.filter(post=post))
        assert versions == [v3, v2, v1]

    def test_cascade_delete_with_post(self):
        version = PostVersionFactory()
        post_pk = version.post.pk
        version.post.delete()
        assert not PostVersion.objects.filter(post_id=post_pk).exists()

    def test_str_representation(self):
        version = PostVersionFactory(version_number=2)
        assert str(version) == f"{version.post} — v2"
