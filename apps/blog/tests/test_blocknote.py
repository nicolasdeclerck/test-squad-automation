import pytest
from django.test import Client

from apps.accounts.tests.factories import UserFactory
from apps.blog.forms import PostForm
from apps.blog.models import Post

from .factories import PostFactory


@pytest.mark.django_db
class TestBlockNoteWidget:
    def test_post_form_widget_renders_blocknote_container(self):
        form = PostForm()
        rendered = form.as_p()
        assert 'id="blocknote-container"' in rendered
        assert 'type="hidden"' in rendered


@pytest.mark.django_db
class TestPostCreateWithHTML:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)

    def test_post_create_with_html_content(self):
        self.client.login(username=self.user.username, password=self.password)
        html_content = "<p>Contenu <strong>riche</strong> de l'article</p>"
        response = self.client.post(
            "/articles/creer/",
            {"title": "Article HTML", "content": html_content},
        )
        post = Post.objects.get(title="Article HTML")
        assert post.content == html_content

    def test_post_update_loads_existing_html(self):
        post = PostFactory(
            author=self.user,
            content="<p>Contenu existant</p>",
        )
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(f"/articles/{post.slug}/modifier/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "&lt;p&gt;Contenu existant&lt;/p&gt;" in content


@pytest.mark.django_db
class TestLegacyPlainTextDisplay:
    def setup_method(self):
        self.client = Client()

    def test_legacy_plain_text_display(self):
        post = PostFactory(content="Ceci est du texte brut sans HTML.")
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert "whitespace-pre-line" in content
        assert "Ceci est du texte brut sans HTML." in content

    def test_html_content_uses_prose(self):
        post = PostFactory(content="<p>Contenu HTML</p>")
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert "prose" in content


@pytest.mark.django_db
class TestHTMLSanitization:
    def test_html_sanitization_removes_script(self):
        post = PostFactory(
            content='<p>Texte</p><script>alert("xss")</script>',
        )
        assert "<script>" not in post.content_sanitized
        assert "<p>Texte</p>" in post.content_sanitized

    def test_html_sanitization_keeps_allowed_tags(self):
        post = PostFactory(
            content="<p>Paragraphe</p><strong>Gras</strong><em>Italique</em>",
        )
        sanitized = post.content_sanitized
        assert "<p>Paragraphe</p>" in sanitized
        assert "<strong>Gras</strong>" in sanitized
        assert "<em>Italique</em>" in sanitized

    def test_html_sanitization_filters_data_uri(self):
        post = PostFactory(
            content='<img src="data:image/png;base64,abc" alt="test">',
        )
        sanitized = post.content_sanitized
        assert "data:image" not in sanitized

    def test_html_sanitization_allows_https_img(self):
        post = PostFactory(
            content='<img src="https://example.com/img.jpg" alt="photo">',
        )
        sanitized = post.content_sanitized
        assert "https://example.com/img.jpg" in sanitized

    def test_is_html_content_true_for_html(self):
        post = PostFactory(content="<p>Du HTML</p>")
        assert post.is_html_content is True

    def test_is_html_content_false_for_plain_text(self):
        post = PostFactory(content="Du texte brut sans balises.")
        assert post.is_html_content is False
