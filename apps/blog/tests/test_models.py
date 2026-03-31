import pytest

from apps.blog.models import Post

from .factories import PostFactory


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
