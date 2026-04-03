import pytest

from apps.blog.forms import BlockNoteWidget, CommentForm, PostForm


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


@pytest.mark.django_db
class TestBlockNoteWidget:
    def test_post_form_widget_renders_blocknote_container(self):
        form = PostForm()
        rendered = form.as_p()
        assert "blocknote-container" in rendered
        assert 'id="blocknote-editor-content"' in rendered

    def test_post_form_widget_is_hidden_input(self):
        form = PostForm()
        widget = form.fields["content"].widget
        assert isinstance(widget, BlockNoteWidget)


@pytest.mark.django_db
class TestCommentForm:
    def test_valid_with_content(self):
        form = CommentForm(data={"content": "Un commentaire"})
        assert form.is_valid()

    def test_invalid_with_empty_content(self):
        form = CommentForm(data={"content": ""})
        assert not form.is_valid()
        assert "content" in form.errors
