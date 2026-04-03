import json

import pytest

from apps.blog.forms import CommentForm, PostForm


VALID_BLOCKNOTE_CONTENT = [
    {"type": "paragraph", "content": [{"type": "text", "text": "Du contenu"}]}
]


@pytest.mark.django_db
class TestPostForm:
    def test_valid_form(self):
        form = PostForm(
            data={
                "title": "Un titre",
                "content": json.dumps(VALID_BLOCKNOTE_CONTENT),
            }
        )
        assert form.is_valid()

    def test_title_required(self):
        form = PostForm(
            data={
                "title": "",
                "content": json.dumps(VALID_BLOCKNOTE_CONTENT),
            }
        )
        assert not form.is_valid()
        assert "title" in form.errors

    def test_content_required(self):
        form = PostForm(data={"title": "Un titre", "content": ""})
        assert not form.is_valid()
        assert "content" in form.errors

    def test_content_must_be_list(self):
        form = PostForm(
            data={
                "title": "Un titre",
                "content": json.dumps({"type": "paragraph"}),
            }
        )
        assert not form.is_valid()
        assert "content" in form.errors

    def test_content_blocks_must_have_type(self):
        form = PostForm(
            data={
                "title": "Un titre",
                "content": json.dumps([{"content": []}]),
            }
        )
        assert not form.is_valid()
        assert "content" in form.errors

    def test_content_valid_blocknote_structure(self):
        content = [
            {
                "type": "heading",
                "content": [{"type": "text", "text": "Titre"}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Paragraphe"}],
            },
        ]
        form = PostForm(
            data={"title": "Un titre", "content": json.dumps(content)}
        )
        assert form.is_valid()

    def test_empty_list_rejected(self):
        form = PostForm(
            data={"title": "Un titre", "content": json.dumps([])}
        )
        assert not form.is_valid()
        assert "content" in form.errors


@pytest.mark.django_db
class TestCommentForm:
    def test_valid_with_content(self):
        form = CommentForm(data={"content": "Un commentaire"})
        assert form.is_valid()

    def test_invalid_with_empty_content(self):
        form = CommentForm(data={"content": ""})
        assert not form.is_valid()
        assert "content" in form.errors
