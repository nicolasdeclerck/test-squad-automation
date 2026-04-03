from django import forms
from django.utils.html import format_html

from .models import Comment, Post


class BlockNoteWidget(forms.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        hidden_html = super().render(name, value, attrs, renderer)
        final_attrs = self.build_attrs(attrs, extra_attrs={"id": (attrs or {}).get("id", f"id_{name}")})
        widget_id = final_attrs["id"]
        container = format_html(
            '<div id="blocknote-{}" class="border border-gray-300'
            " rounded min-h-[300px] focus-within:ring-1 focus-within:ring-black"
            ' focus-within:border-black"></div>',
            widget_id,
        )
        return hidden_html + container


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
