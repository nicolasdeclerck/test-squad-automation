from django import forms
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import Comment, Post


class BlockNoteWidget(forms.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        widget_id = attrs.get("id", f"id_{name}")
        value_attr = f' value="{escape(value)}"' if value else ""
        return mark_safe(
            f'<input type="hidden" name="{name}" id="{widget_id}"{value_attr}>'
            f'<div id="blocknote-container" class="border border-gray-300'
            f" rounded min-h-[300px] focus-within:ring-1 focus-within:ring-black"
            f' focus-within:border-black"></div>'
        )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content")
        widgets = {
            "content": BlockNoteWidget,
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
