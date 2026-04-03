import pytest

from apps.blog.models import Comment, Post

from .factories import CommentFactory, PostFactory


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

    def test_content_stores_json(self):
        content = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Hello"}],
            }
        ]
        post = PostFactory(content=content)
        post.refresh_from_db()
        assert post.content == content
        assert isinstance(post.content, list)

    def test_content_default_is_list(self):
        post = PostFactory(content=[])
        post.refresh_from_db()
        assert post.content == []


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
