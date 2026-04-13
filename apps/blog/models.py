from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, UnidentifiedImageError


def validate_post_image(image):
    max_size = 10 * 1024 * 1024  # 10 MB
    try:
        file_size = image.size
    except (FileNotFoundError, OSError, ValueError, AttributeError):
        raise ValidationError("Le fichier image est inaccessible.")
    if file_size > max_size:
        raise ValidationError(
            "La taille de l'image ne doit pas dépasser 10 Mo."
        )

    try:
        if hasattr(image, "seek"):
            image.seek(0)
        if hasattr(image, "read"):
            data = BytesIO(image.read())
            image.seek(0)
        elif hasattr(image, "temporary_file_path"):
            data = image.temporary_file_path()
        else:
            raise UnidentifiedImageError("Impossible de lire le fichier.")
        img = Image.open(data)
        img.verify()
        allowed_formats = {"JPEG", "PNG", "WEBP", "GIF"}
        if img.format not in allowed_formats:
            raise ValidationError(
                "Format non autorisé. Utilisez JPEG, PNG, WebP ou GIF."
            )
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ValidationError(
            "Format non autorisé. Utilisez JPEG, PNG, WebP ou GIF."
        )


def validate_post_video(video):
    max_size = 50 * 1024 * 1024  # 50 MB
    try:
        file_size = video.size
    except (FileNotFoundError, OSError, ValueError, AttributeError):
        raise ValidationError("Le fichier vidéo est inaccessible.")
    if file_size > max_size:
        raise ValidationError(
            "La taille de la vidéo ne doit pas dépasser 50 Mo."
        )

    import os

    allowed_extensions = {".mp4", ".webm", ".ogg", ".ogv"}
    name = getattr(video, "name", "")
    _, ext = os.path.splitext(name.lower())
    if ext not in allowed_extensions:
        raise ValidationError(
            "Format non autorisé. Utilisez MP4, WebM ou OGG."
        )


class PostVideo(models.Model):
    video = models.FileField(
        upload_to="blog/videos/",
        validators=[validate_post_video],
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_videos",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video {self.pk} par {self.uploaded_by}"


class PostImage(models.Model):
    image = models.ImageField(
        upload_to="blog/images/",
        validators=[validate_post_image],
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_images",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.pk} par {self.uploaded_by}"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "tag"
            slug = base_slug
            counter = 1
            while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


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
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
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
        self.title = self.draft_title or self.title
        self.content = self.draft_content or self.content
        self.status = self.STATUS_PUBLISHED
        self.has_draft = False
        self.draft_title = ""
        self.draft_content = ""
        if not self.published_at:
            self.published_at = timezone.now()
        self.save()

        current_max = self.versions.aggregate(max_num=Max("version_number"))[
            "max_num"
        ]
        next_version = (current_max or 0) + 1
        PostVersion.objects.create(
            post=self,
            version_number=next_version,
            title=self.title,
            content=self.content,
            published_at=timezone.now(),
            created_by=self.author,
        )

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
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "version_number"],
                name="unique_post_version_number",
            )
        ]
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
