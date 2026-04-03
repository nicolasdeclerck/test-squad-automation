from django import forms
from django.utils.safestring import mark_safe

from .models import Comment, Post


class BlockNoteWidget(forms.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        hidden_input = forms.HiddenInput.render(
            self, name, value, attrs, renderer=renderer
        )
        editor_id = f"blocknote-editor-{name}"
        html = (
            f'<div id="{editor_id}" class="blocknote-container border'
            f' border-gray-300 rounded-md min-h-[300px]"></div>'
            f"{hidden_input}"
        )
        return mark_safe(html)

    class Media:
        js = ("js/dist/blocknote-editor.iife.js",)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content")
        widgets = {
            "content": BlockNoteWidget(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Écrivez votre commentaire...",
                    "class": (
                        "w-full px-3 py-2 border border-gray-300 rounded-md"
                        " focus:outline-none focus:ring-1 focus:ring-gray-900"
                    ),
                }
            ),
        }
