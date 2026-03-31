import pytest

from apps.blog.forms import PostForm


@pytest.mark.django_db
class TestPostForm:
    def test_valid_form(self):
        form = PostForm(data={"title": "Un titre", "content": "Du contenu"})
        assert form.is_valid()

    def test_title_required(self):
        form = PostForm(data={"title": "", "content": "Du contenu"})
        assert not form.is_valid()
        assert "title" in form.errors

    def test_content_required(self):
        form = PostForm(data={"title": "Un titre", "content": ""})
        assert not form.is_valid()
        assert "content" in form.errors
