from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def validate_avatar(image):
    if not image:
        return

    max_size = 5 * 1024 * 1024  # 5 MB
    try:
        file_size = image.size
    except (FileNotFoundError, OSError, ValueError):
        raise ValidationError("Le fichier image est inaccessible.")
    if file_size > max_size:
        raise ValidationError("La taille de l'image ne doit pas dépasser 5 Mo.")

    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    content_type = getattr(image, "content_type", None)
    if content_type and content_type not in allowed_types:
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
        validators=[validate_avatar],
    )

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"Profil de {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
