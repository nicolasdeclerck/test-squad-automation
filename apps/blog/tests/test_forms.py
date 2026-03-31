import json

import pytest

from apps.blog.forms import PostForm
from apps.blog.tests.factories import CategoryFactory

pytestmark = pytest.mark.django_db


class TestPostForm:
    def test_valid_form_with_json_content(self):
        category = CategoryFactory()
        blocks = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Contenu"}],
            }
        ]
        form = PostForm(
            data={
                "title": "Test article",
                "category": category.pk,
                "status": "draft",
                "content_json": json.dumps(blocks),
                "content": "<p>Contenu</p>",
            }
        )
        assert form.is_valid(), form.errors

    def test_valid_form_with_empty_json(self):
        form = PostForm(
            data={
                "title": "Test article",
                "status": "draft",
                "content_json": "",
                "content": "",
            }
        )
        assert form.is_valid(), form.errors

    def test_invalid_json_rejected(self):
        form = PostForm(
            data={
                "title": "Test article",
                "status": "draft",
                "content_json": "not valid json{{{",
                "content": "",
            }
        )
        assert not form.is_valid()
        assert "content_json" in form.errors

    def test_non_object_json_rejected(self):
        form = PostForm(
            data={
                "title": "Test article",
                "status": "draft",
                "content_json": '"just a string"',
                "content": "",
            }
        )
        assert not form.is_valid()
        assert "content_json" in form.errors

    def test_content_and_content_json_are_hidden_inputs(self):
        form = PostForm()
        assert form.fields["content"].widget.input_type == "hidden"
        assert form.fields["content_json"].widget.input_type == "hidden"
