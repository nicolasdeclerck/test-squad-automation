import json

from django import forms

from apps.blog.models import Post


class PostForm(forms.ModelForm):
    content_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
    content = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "category",
            "tags",
            "excerpt",
            "cover_image",
            "status",
            "content",
            "content_json",
        ]

    def clean_content_json(self):
        raw = self.cleaned_data.get("content_json")
        if not raw:
            return {}
        if isinstance(raw, (dict, list)):
            return raw
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            raise forms.ValidationError(
                "Le contenu JSON de l'éditeur est invalide."
            )
        if not isinstance(data, (dict, list)):
            raise forms.ValidationError(
                "Le contenu JSON doit être un objet ou une liste."
            )
        return data
