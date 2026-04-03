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


@pytest.mark.django_db
class TestPostContentSanitization:
    def test_html_sanitization_strips_script(self):
        post = PostFactory(content='<p>Hello</p><script>alert("xss")</script>')
        assert "<script>" not in post.content_sanitized
        assert "<p>Hello</p>" in post.content_sanitized

    def test_html_sanitization_allows_safe_tags(self):
        html = "<p><strong>Bold</strong> and <em>italic</em></p>"
        post = PostFactory(content=html)
        assert post.content_sanitized == html

    def test_html_sanitization_allows_links(self):
        html = '<p><a href="https://example.com">Link</a></p>'
        post = PostFactory(content=html)
        assert 'href="https://example.com"' in post.content_sanitized

    def test_html_sanitization_strips_onclick(self):
        html = '<p onclick="alert(1)">Text</p>'
        post = PostFactory(content=html)
        assert "onclick" not in post.content_sanitized
        assert "<p>Text</p>" in post.content_sanitized


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
