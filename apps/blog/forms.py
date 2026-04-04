from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content")
        widgets = {
            "content": forms.HiddenInput(),
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
