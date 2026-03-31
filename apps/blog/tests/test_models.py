import pytest

from apps.blog.models import Post
from apps.blog.tests.factories import (
    CategoryFactory,
    CommentFactory,
    PostFactory,
    TagFactory,
)

pytestmark = pytest.mark.django_db


class TestCategory:
    def test_str(self):
        category = CategoryFactory(name="Python")
        assert str(category) == "Python"


class TestTag:
    def test_str(self):
        tag = TagFactory(name="Django")
        assert str(tag) == "Django"


class TestPost:
    def test_str(self):
        post = PostFactory(title="Mon article")
        assert str(post) == "Mon article"

    def test_slug_auto_generated(self):
        post = PostFactory(title="Mon super article", slug="")
        assert post.slug == "mon-super-article"

    def test_content_json_saved_and_retrieved(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Hello world"}],
            }
        ]
        post = PostFactory(content_json=blocks)
        post.refresh_from_db()
        assert post.content_json == blocks

    def test_content_html_generated_from_json_on_save(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Hello world"}],
            }
        ]
        post = PostFactory(content_json=blocks, content="")
        post.refresh_from_db()
        assert "<p>Hello world</p>" in post.content

    def test_content_html_with_heading(self):
        blocks = [
            {
                "type": "heading",
                "props": {"level": 2},
                "content": [{"type": "text", "text": "Titre"}],
            }
        ]
        post = PostFactory(content_json=blocks, content="")
        post.refresh_from_db()
        assert "<h2>Titre</h2>" in post.content

    def test_content_html_with_bold_italic(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "gras",
                        "styles": {"bold": True},
                    },
                    {
                        "type": "text",
                        "text": " et ",
                    },
                    {
                        "type": "text",
                        "text": "italique",
                        "styles": {"italic": True},
                    },
                ],
            }
        ]
        post = PostFactory(content_json=blocks, content="")
        post.refresh_from_db()
        assert "<strong>gras</strong>" in post.content
        assert "<em>italique</em>" in post.content

    def test_empty_content_json_does_not_overwrite_content(self):
        post = PostFactory(content_json={}, content="<p>Existing</p>")
        post.refresh_from_db()
        assert post.content == "<p>Existing</p>"

    def test_ordering(self):
        post1 = PostFactory()
        post2 = PostFactory()
        posts = list(Post.objects.all())
        assert posts[0] == post2
        assert posts[1] == post1


class TestComment:
    def test_str(self):
        comment = CommentFactory()
        assert str(comment).startswith("Commentaire de")

    def test_default_not_approved(self):
        comment = CommentFactory()
        assert comment.is_approved is False
