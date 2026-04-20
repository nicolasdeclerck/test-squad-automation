import json
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from PIL import Image

from apps.blog.og import build_meta_tags, extract_excerpt, inject_into_head

from .factories import PostFactory

INDEX_HTML = (
    "<!DOCTYPE html>\n"
    '<html lang="fr">\n'
    "  <head>\n"
    '    <meta charset="UTF-8" />\n'
    "    <title>NICKORP</title>\n"
    "  </head>\n"
    '  <body><div id="root"></div></body>\n'
    "</html>\n"
)


@pytest.fixture
def index_html(tmp_path):
    path = tmp_path / "index.html"
    path.write_text(INDEX_HTML, encoding="utf-8")
    return path


def _cover_image():
    buf = BytesIO()
    Image.new("RGB", (1200, 630), (10, 20, 30)).save(buf, format="JPEG")
    return SimpleUploadedFile("cover.jpg", buf.getvalue(), content_type="image/jpeg")


class TestExtractExcerpt:
    def test_returns_empty_for_empty_input(self):
        assert extract_excerpt("") == ""
        assert extract_excerpt(None) == ""

    def test_extracts_plain_text_from_blocknote_json(self):
        blocks = json.dumps(
            [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Hello "},
                        {"type": "text", "text": "world"},
                    ],
                }
            ]
        )
        assert extract_excerpt(blocks) == "Hello world"

    def test_joins_multiple_blocks_with_single_space(self):
        blocks = json.dumps(
            [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "First block."}],
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Second block."}],
                },
            ]
        )
        assert extract_excerpt(blocks) == "First block. Second block."

    def test_walks_nested_children(self):
        blocks = json.dumps(
            [
                {
                    "type": "list",
                    "content": [],
                    "children": [
                        {
                            "type": "item",
                            "content": [{"type": "text", "text": "nested"}],
                        }
                    ],
                }
            ]
        )
        assert extract_excerpt(blocks) == "nested"

    def test_falls_back_to_raw_text_when_not_json(self):
        assert extract_excerpt("plain text content") == "plain text content"

    def test_truncates_long_text_with_ellipsis(self):
        long = "mot " * 200
        result = extract_excerpt(long, max_chars=50)
        assert len(result) <= 51
        assert result.endswith("…")


@pytest.mark.django_db
class TestBuildMetaTags:
    def test_includes_all_required_tags_with_cover(self):
        post = PostFactory(title="Mon article", content="Résumé du contenu")
        post.cover_image = _cover_image()
        post.save()
        post.refresh_from_db()

        meta = build_meta_tags(
            post=post,
            canonical_url="https://blog.example.com/articles/mon-article/",
            default_image_url="/static/og/default.png",
            base_url="https://blog.example.com",
        )

        assert 'property="og:type" content="article"' in meta
        assert 'property="og:title" content="Mon article"' in meta
        assert 'property="og:description" content="Résumé du contenu"' in meta
        assert (
            'property="og:url" content="https://blog.example.com/articles/mon-article/"'
            in meta
        )
        assert 'property="og:image"' in meta
        assert "/media/blog/covers/" in meta
        assert 'name="twitter:card" content="summary_large_image"' in meta
        assert 'name="twitter:title" content="Mon article"' in meta
        assert 'name="twitter:image"' in meta
        assert 'rel="canonical"' in meta

    def test_falls_back_to_default_image_when_no_cover(self):
        post = PostFactory(title="Sans couverture", content="x")
        meta = build_meta_tags(
            post=post,
            canonical_url="https://blog.example.com/articles/sans-couverture/",
            default_image_url="/static/og/default.png",
            base_url="https://blog.example.com",
        )
        assert (
            'property="og:image" content="https://blog.example.com/static/og/default.png"'
            in meta
        )

    def test_escapes_html_in_title(self):
        post = PostFactory(title='Tag <script>"', content="x")
        meta = build_meta_tags(
            post=post,
            canonical_url="https://example.com/articles/x/",
            default_image_url="/default.png",
            base_url="https://example.com",
        )
        assert "<script>" not in meta
        assert "&lt;script&gt;" in meta
        assert "&quot;" in meta


class TestInjectIntoHead:
    def test_injects_before_closing_head(self):
        html = "<html><head><title>x</title></head><body></body></html>"
        out = inject_into_head(html, '<meta name="robots" content="noindex">')
        assert '<meta name="robots" content="noindex">' in out
        assert out.index("<meta") < out.index("</head>")

    def test_returns_input_unchanged_when_no_head(self):
        html = "<html><body></body></html>"
        assert inject_into_head(html, "<meta>") == html


@pytest.mark.django_db
class TestArticleOGView:
    def setup_method(self):
        self.client = Client()

    def _url(self, slug):
        return f"/articles/{slug}/"

    def test_published_post_injects_og_tags(self, index_html):
        post = PostFactory(title="Article pub", content="Texte pub")
        with override_settings(
            FRONTEND_INDEX_HTML=str(index_html),
            SITE_URL="https://blog.example.com",
            DEFAULT_OG_IMAGE_URL="/static/og/default.png",
        ):
            response = self.client.get(self._url(post.slug))

        assert response.status_code == 200
        assert response["Content-Type"] == "text/html; charset=utf-8"
        assert response["Cache-Control"] == "public, max-age=300"
        assert "X-Robots-Tag" not in response
        body = response.content.decode("utf-8")
        assert 'property="og:title" content="Article pub"' in body
        assert 'property="og:description" content="Texte pub"' in body
        assert (
            f'property="og:url" content="https://blog.example.com/articles/{post.slug}/"'
            in body
        )
        assert "<title>Article pub</title>" in body

    def test_published_post_without_cover_uses_default_image(self, index_html):
        post = PostFactory(title="Pas de cover", content="x")
        with override_settings(
            FRONTEND_INDEX_HTML=str(index_html),
            SITE_URL="https://blog.example.com",
            DEFAULT_OG_IMAGE_URL="/static/og/default.png",
        ):
            response = self.client.get(self._url(post.slug))

        body = response.content.decode("utf-8")
        assert (
            'property="og:image" content="https://blog.example.com/static/og/default.png"'
            in body
        )

    def test_draft_post_serves_plain_html_without_og(self, index_html):
        post = PostFactory(
            title="Brouillon",
            content="x",
            status="draft",
            published_at=None,
        )
        with override_settings(
            FRONTEND_INDEX_HTML=str(index_html),
            SITE_URL="https://blog.example.com",
            DEFAULT_OG_IMAGE_URL="/static/og/default.png",
        ):
            response = self.client.get(self._url(post.slug))

        assert response.status_code == 200
        assert response["X-Robots-Tag"] == "noindex"
        assert response["Cache-Control"] == "no-store"
        body = response.content.decode("utf-8")
        assert "og:title" not in body
        assert "<title>NICKORP</title>" in body

    def test_reserved_slug_returns_fallback_with_noindex(self, index_html):
        with override_settings(
            FRONTEND_INDEX_HTML=str(index_html),
            SITE_URL="https://blog.example.com",
            DEFAULT_OG_IMAGE_URL="/static/og/default.png",
        ):
            response = self.client.get(self._url("creer"))

        assert response.status_code == 200
        assert response["X-Robots-Tag"] == "noindex"
        assert "og:title" not in response.content.decode("utf-8")

    def test_unknown_slug_returns_plain_html(self, index_html):
        with override_settings(
            FRONTEND_INDEX_HTML=str(index_html),
            SITE_URL="https://blog.example.com",
            DEFAULT_OG_IMAGE_URL="/static/og/default.png",
        ):
            response = self.client.get(self._url("does-not-exist"))

        assert response.status_code == 200
        assert "og:title" not in response.content.decode("utf-8")

    def test_missing_index_html_returns_503(self, tmp_path):
        with override_settings(
            FRONTEND_INDEX_HTML=str(tmp_path / "missing.html"),
            SITE_URL="https://blog.example.com",
            DEFAULT_OG_IMAGE_URL="/static/og/default.png",
        ):
            response = self.client.get(self._url("any"))
        assert response.status_code == 503
