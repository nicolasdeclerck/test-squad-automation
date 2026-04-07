from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Post(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_PUBLISHED, "Publié"),
    ]

    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    content = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    draft_title = models.CharField(max_length=200, blank=True)
    draft_content = models.TextField(blank=True)
    has_draft = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or self.draft_title or "(sans titre)"

    def publish(self):
        self.title = self.draft_title
        self.content = self.draft_content
        self.status = self.STATUS_PUBLISHED
        self.has_draft = False
        self.draft_title = ""
        self.draft_content = ""
        if not self.published_at:
            self.published_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            source_title = self.draft_title or self.title or "article"
            base_slug = slugify(source_title)
            if not base_slug:
                base_slug = "article"
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class PostVersion(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="versions"
    )
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [("post", "version_number")]
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.post} — v{self.version_number}"


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
