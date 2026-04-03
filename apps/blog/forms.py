from django import forms
from django.utils.html import format_html

from .models import Comment, Post


class BlockNoteWidget(forms.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        widget_id = attrs.get("id", f"id_{name}")
        return format_html(
            '<input type="hidden" name="{}" id="{}" value="{}">'
            '<div id="blocknote-{}" class="border border-gray-300'
            " rounded min-h-[300px] focus-within:ring-1 focus-within:ring-black"
            ' focus-within:border-black"></div>',
            name,
            widget_id,
            value or "",
            widget_id,
        )


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
