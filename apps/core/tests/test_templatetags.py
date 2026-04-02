import pytest
from django.template import Context, Template
from django.test import Client

from apps.accounts.tests.factories import UserFactory
from apps.blog.tests.factories import PostFactory


class TestRenderMarkdownFilter:
    def test_renders_bold(self):
        template = Template(
            '{% load markdown_extras %}{{ text|render_markdown }}'
        )
        result = template.render(Context({"text": "**bold**"}))
        assert "<strong>bold</strong>" in result

    def test_renders_heading(self):
        template = Template(
            '{% load markdown_extras %}{{ text|render_markdown }}'
        )
        result = template.render(Context({"text": "# Title"}))
        assert "<h1>Title</h1>" in result

    def test_renders_fenced_code_block(self):
        template = Template(
            '{% load markdown_extras %}{{ text|render_markdown }}'
        )
        code = "```python\nprint('hello')\n```"
        result = template.render(Context({"text": code}))
        assert "codehilite" in result

    def test_strips_dangerous_tags(self):
        template = Template(
            '{% load markdown_extras %}{{ text|render_markdown }}'
        )
        result = template.render(
            Context({"text": "<script>alert('xss')</script>"})
        )
        assert "<script>" not in result

    def test_renders_links(self):
        template = Template(
            '{% load markdown_extras %}{{ text|render_markdown }}'
        )
        result = template.render(
            Context({"text": "[link](https://example.com)"})
        )
        assert 'href="https://example.com"' in result
        assert ">link</a>" in result


@pytest.mark.django_db
class TestPostDetailMetaDescription:
    def setup_method(self):
        self.client = Client()

    def test_meta_description_strips_markdown(self):
        post = PostFactory(content="**bold** and # title and `code`")
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert "**bold**" not in content.split('name="description"')[1].split(">")[0]
        assert "**" not in content.split('name="description"')[1].split(">")[0]

    def test_meta_description_no_html_tags(self):
        post = PostFactory(content="**bold** text with [link](http://example.com)")
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        meta_section = content.split('content="')[1].split('"')[0]
        assert "<strong>" not in meta_section
        assert "<a " not in meta_section
