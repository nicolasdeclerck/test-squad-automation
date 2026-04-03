from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content")
        widgets = {
            "content": forms.HiddenInput(),
        }

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if not content:
            raise ValidationError("Le contenu ne peut pas être vide.")
        if not isinstance(content, list):
            raise ValidationError(
                "Le contenu doit être une liste de blocs."
            )
        for block in content:
            if not isinstance(block, dict) or "type" not in block:
                raise ValidationError(
                    "Chaque bloc doit être un objet avec un champ 'type'."
                )
        return content


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
