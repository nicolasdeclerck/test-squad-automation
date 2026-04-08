import os
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image, UnidentifiedImageError


def validate_avatar(image):
    if not image:
        return

    max_size = 5 * 1024 * 1024  # 5 MB
    try:
        file_size = image.size
    except (FileNotFoundError, OSError, ValueError, AttributeError):
        raise ValidationError("Le fichier image est inaccessible.")
    if file_size > max_size:
        raise ValidationError("La taille de l'image ne doit pas dépasser 5 Mo.")

    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    content_type = getattr(image, "content_type", None)
    if content_type and content_type not in allowed_types:
        raise ValidationError(
            "Format non autorisé. Utilisez JPEG, PNG ou WebP."
        )

    # Vérification du contenu réel avec PIL
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
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ValidationError(
            "Format non autorisé. Utilisez JPEG, PNG ou WebP."
        )


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        validators=[validate_avatar],
    )

    AVATAR_MAX_SIZE = (300, 300)
    AVATAR_JPEG_QUALITY = 85

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"Profil de {self.user.username}"

    def _compress_avatar(self):
        """Compress and resize avatar to JPEG, max 300x300."""
        img = Image.open(self.avatar)
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.convert("RGBA").split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail(self.AVATAR_MAX_SIZE, Image.LANCZOS)

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=self.AVATAR_JPEG_QUALITY, optimize=True)

        name = os.path.splitext(os.path.basename(self.avatar.name))[0] + ".jpg"
        self.avatar.save(name, ContentFile(buf.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_avatar = Profile.objects.get(pk=self.pk).avatar.name
            except Profile.DoesNotExist:
                old_avatar = None
        else:
            old_avatar = None

        if self.avatar and self.avatar.name != old_avatar:
            self._compress_avatar()

        super().save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
