import pytest

from apps.core.templatetags.markdown_extras import markdown_filter


class TestMarkdownFilter:
    def test_markdown_filter_renders_basic_markdown(self):
        result = markdown_filter("**bold** and *italic*")
        assert "<strong>bold</strong>" in result
        assert "<em>italic</em>" in result

    def test_markdown_filter_renders_headings(self):
        result = markdown_filter("# Titre")
        assert "<h1>Titre</h1>" in result

    def test_markdown_filter_renders_links(self):
        result = markdown_filter("[lien](https://example.com)")
        assert '<a href="https://example.com">lien</a>' in result

    def test_markdown_filter_sanitizes_xss(self):
        result = markdown_filter('<script>alert("xss")</script>')
        assert "<script>" not in result
        assert "</script>" not in result

    def test_markdown_filter_sanitizes_onclick(self):
        result = markdown_filter('<a href="#" onclick="alert(1)">click</a>')
        assert "onclick" not in result

    def test_markdown_filter_supports_fenced_code(self):
        md_text = "```python\nprint('hello')\n```"
        result = markdown_filter(md_text)
        assert "<code>" in result
        assert "print" in result

    def test_markdown_filter_supports_tables(self):
        md_text = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = markdown_filter(md_text)
        assert "<table>" in result
        assert "<td>" in result

    def test_markdown_filter_returns_safe_string(self):
        result = markdown_filter("hello")
        assert hasattr(result, "__html__")
