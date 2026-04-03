import re

import nh3
from django.conf import settings
from django.db import models
from django.utils.text import slugify

ALLOWED_TAGS = {
    "p", "h1", "h2", "h3", "ul", "ol", "li", "strong", "em",
    "a", "img", "blockquote", "code", "pre", "br", "span", "div",
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt"},
}


class Post(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_PUBLISHED, "Publié"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    content = models.TextField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_PUBLISHED
    )
    published_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_html_content(self):
        """Détecte si le contenu est du HTML (vs texte brut legacy)."""
        return bool(re.search(r"<[a-z][\s\S]*>", self.content))

    @property
    def content_sanitized(self):
        return nh3.clean(
            self.content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            url_schemes={"http", "https"},
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Commentaire de {self.author} sur {self.post}"
