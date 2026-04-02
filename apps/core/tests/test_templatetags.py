import pytest
from django.template import Context, Template


class TestRenderMarkdownFilter:
    def _render(self, value):
        template = Template("{% load markdown_extras %}{{ content|render_markdown }}")
        return template.render(Context({"content": value}))

    def test_renders_bold(self):
        result = self._render("**bold text**")
        assert "<strong>bold text</strong>" in result

    def test_renders_italic(self):
        result = self._render("*italic text*")
        assert "<em>italic text</em>" in result

    def test_renders_heading(self):
        result = self._render("## Heading")
        assert "<h2>" in result

    def test_renders_link(self):
        result = self._render("[link](https://example.com)")
        assert 'href="https://example.com"' in result
        assert ">link</a>" in result

    def test_sanitizes_script_tags(self):
        result = self._render("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "alert" not in result

    def test_sanitizes_onclick(self):
        result = self._render('<a href="#" onclick="alert(1)">click</a>')
        assert "onclick" not in result

    def test_renders_code_block(self):
        result = self._render("```\ncode\n```")
        assert "<code>" in result

    def test_renders_list(self):
        result = self._render("- item 1\n- item 2")
        assert "<li>" in result
        assert "<ul>" in result

    def test_empty_string(self):
        result = self._render("")
        assert result.strip() == ""

    def test_none_value(self):
        result = self._render(None)
        assert result.strip() == ""
