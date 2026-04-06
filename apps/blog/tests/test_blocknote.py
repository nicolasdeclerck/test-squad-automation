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

BLOCKNOTE_MERMAID_CONTENT = json.dumps(
    [
        {
            "id": "1",
            "type": "paragraph",
            "props": {},
            "content": [{"type": "text", "text": "Voici un diagramme :"}],
            "children": [],
        },
        {
            "id": "2",
            "type": "mermaid",
            "props": {"data": "graph TD\n    A[Début] --> B[Fin]"},
            "content": [],
            "children": [],
        },
        {
            "id": "3",
            "type": "paragraph",
            "props": {},
            "content": [{"type": "text", "text": "Fin de l'article."}],
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


@pytest.mark.django_db
class TestBlockNoteDisplayInListings:
    """Verify that listing pages show readable text, not raw JSON."""

    def setup_method(self):
        self.client = Client()
        self.post = PostFactory(content=BLOCKNOTE_JSON_CONTENT)

    def test_home_displays_plaintext_not_json(self):
        response = self.client.get("/")
        content = response.content.decode()
        assert "Mon titre" in content
        assert '"type"' not in content
        assert '"heading"' not in content

    def test_post_list_displays_plaintext_not_json(self):
        response = self.client.get("/articles/")
        content = response.content.decode()
        assert "Mon titre" in content
        assert '"type"' not in content
        assert '"heading"' not in content

    def test_detail_noscript_displays_plaintext(self):
        response = self.client.get(f"/articles/{self.post.slug}/")
        content = response.content.decode()
        noscript_start = content.find("<noscript>")
        noscript_end = content.find("</noscript>")
        assert noscript_start != -1, "noscript block not found in post_detail"
        assert noscript_end != -1, "noscript closing tag not found"
        noscript_content = content[noscript_start:noscript_end]
        assert '"type"' not in noscript_content
        assert "Mon titre" in noscript_content

    def test_home_displays_legacy_plaintext_content(self):
        PostFactory(content="Contenu texte brut legacy")
        response = self.client.get("/")
        content = response.content.decode()
        assert "Contenu texte brut legacy" in content


@pytest.mark.django_db
class TestBlockNoteMermaidCreate:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)

    def test_create_post_with_mermaid_content(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            CREATE_URL,
            {"title": "Article Mermaid", "content": BLOCKNOTE_MERMAID_CONTENT},
        )
        assert response.status_code == 302
        post = Post.objects.get(title="Article Mermaid")
        parsed = json.loads(post.content)
        assert isinstance(parsed, list)
        mermaid_blocks = [b for b in parsed if b.get("type") == "mermaid"]
        assert len(mermaid_blocks) == 1
        assert "graph TD" in mermaid_blocks[0]["props"]["data"]


class TestBlockNoteMermaidPlaintext:
    def test_mermaid_plaintext_extraction(self):
        result = blocknote_plaintext(BLOCKNOTE_MERMAID_CONTENT)
        assert "Voici un diagramme :" in result
        assert "[Diagramme Mermaid]" in result
        assert "Fin de l'article." in result

    def test_mermaid_empty_data_excluded(self):
        content = json.dumps(
            [
                {
                    "id": "1",
                    "type": "mermaid",
                    "props": {"data": ""},
                    "content": [],
                    "children": [],
                }
            ]
        )
        result = blocknote_plaintext(content)
        assert "[Diagramme Mermaid]" not in result

    def test_mermaid_block_does_not_leak_raw_code(self):
        result = blocknote_plaintext(BLOCKNOTE_MERMAID_CONTENT)
        assert "graph TD" not in result


@pytest.mark.django_db
class TestBlockNoteMermaidDetail:
    def setup_method(self):
        self.client = Client()

    def test_detail_renders_mermaid_content_in_data_attribute(self):
        post = PostFactory(content=BLOCKNOTE_MERMAID_CONTENT)
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert 'id="blocknote-content"' in content
        assert "data-content" in content
        assert "mermaid" in content
