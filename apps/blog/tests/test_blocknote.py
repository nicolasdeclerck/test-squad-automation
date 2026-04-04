import json

import pytest
from django.test import Client

from apps.accounts.tests.factories import UserFactory
from apps.blog.models import Post
from apps.blog.templatetags.blog_extras import blocknote_plaintext

from .factories import PostFactory

BLOCKNOTE_JSON_CONTENT = json.dumps(
    [
        {
            "id": "1",
            "type": "heading",
            "props": {"level": 2},
            "content": [{"type": "text", "text": "Mon titre"}],
            "children": [],
        },
        {
            "id": "2",
            "type": "paragraph",
            "props": {},
            "content": [
                {"type": "text", "text": "Un paragraphe avec du "},
                {
                    "type": "text",
                    "text": "texte en gras",
                    "styles": {"bold": True},
                },
                {"type": "text", "text": "."},
            ],
            "children": [],
        },
    ]
)

CREATE_URL = "/articles/creer/"
LOGIN_URL = "/comptes/connexion/"


@pytest.mark.django_db
class TestBlockNotePostCreate:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)

    def test_create_post_with_json_content(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            CREATE_URL,
            {"title": "Article BlockNote", "content": BLOCKNOTE_JSON_CONTENT},
        )
        assert response.status_code == 302
        post = Post.objects.get(title="Article BlockNote")
        parsed = json.loads(post.content)
        assert isinstance(parsed, list)
        assert parsed[0]["type"] == "heading"

    def test_create_post_with_plain_text_content(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            CREATE_URL,
            {"title": "Article texte", "content": "Du contenu simple"},
        )
        assert response.status_code == 302
        post = Post.objects.get(title="Article texte")
        assert post.content == "Du contenu simple"


@pytest.mark.django_db
class TestBlockNotePostUpdate:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)
        self.post = PostFactory(
            author=self.user, content=BLOCKNOTE_JSON_CONTENT
        )
        self.url = f"/articles/{self.post.slug}/modifier/"

    def test_update_preserves_json_content(self):
        self.client.login(username=self.user.username, password=self.password)
        new_content = json.dumps(
            [
                {
                    "id": "1",
                    "type": "paragraph",
                    "props": {},
                    "content": [
                        {"type": "text", "text": "Contenu modifie"}
                    ],
                    "children": [],
                }
            ]
        )
        response = self.client.post(
            self.url,
            {"title": self.post.title, "content": new_content},
        )
        assert response.status_code == 302
        self.post.refresh_from_db()
        parsed = json.loads(self.post.content)
        assert parsed[0]["content"][0]["text"] == "Contenu modifie"


@pytest.mark.django_db
class TestBlockNotePostDetail:
    def setup_method(self):
        self.client = Client()

    def test_detail_renders_json_content_in_data_attribute(self):
        post = PostFactory(content=BLOCKNOTE_JSON_CONTENT)
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert 'id="blocknote-content"' in content
        assert "data-content" in content

    def test_detail_renders_plain_text_fallback(self):
        post = PostFactory(content="Contenu texte brut simple")
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert "Contenu texte brut simple" in content

    def test_detail_includes_renderer_script(self):
        post = PostFactory(content=BLOCKNOTE_JSON_CONTENT)
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert "blocknote-renderer.js" in content


@pytest.mark.django_db
class TestBlockNotePostForm:
    def test_post_form_content_is_hidden_input(self):
        from apps.blog.forms import PostForm

        form = PostForm()
        assert form.fields["content"].widget.__class__.__name__ == "HiddenInput"

    def test_post_form_valid_with_json_content(self):
        from apps.blog.forms import PostForm

        form = PostForm(
            data={"title": "Test", "content": BLOCKNOTE_JSON_CONTENT}
        )
        assert form.is_valid()

    def test_post_form_valid_with_plain_text_content(self):
        from apps.blog.forms import PostForm

        form = PostForm(
            data={"title": "Test", "content": "Du texte simple"}
        )
        assert form.is_valid()


class TestBlockNotePlaintext:
    def test_extracts_text_from_blocknote_json(self):
        result = blocknote_plaintext(BLOCKNOTE_JSON_CONTENT)
        assert "Mon titre" in result
        assert "Un paragraphe avec du" in result
        assert "texte en gras" in result

    def test_returns_plain_text_as_is(self):
        assert blocknote_plaintext("Du texte simple") == "Du texte simple"

    def test_returns_empty_string_for_empty_input(self):
        assert blocknote_plaintext("") == ""
        assert blocknote_plaintext(None) == ""

    def test_returns_value_for_invalid_json(self):
        assert blocknote_plaintext("{invalid") == "{invalid"
