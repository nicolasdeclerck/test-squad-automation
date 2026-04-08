from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.accounts.models import Profile, validate_avatar

from .factories import UserFactory

User = get_user_model()


def _make_image(width, height, fmt="JPEG", mode="RGB"):
    """Helper to create a test image as SimpleUploadedFile."""
    buf = BytesIO()
    img = Image.new(mode, (width, height), color="red")
    if fmt == "JPEG" and mode != "RGB":
        img = img.convert("RGB")
    img.save(buf, format=fmt)
    content_type = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}[fmt]
    ext = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}[fmt]
    return SimpleUploadedFile(f"test.{ext}", buf.getvalue(), content_type=content_type)


@pytest.mark.django_db
class TestProfileSignal:
    def test_profile_created_on_user_creation(self):
        user = UserFactory()
        assert hasattr(user, "profile")
        assert isinstance(user.profile, Profile)

    def test_profile_exists_after_user_save(self):
        user = UserFactory()
        user.first_name = "Jean"
        user.save()
        assert Profile.objects.filter(user=user).count() == 1

    def test_signal_does_not_save_profile_on_user_update(self):
        user = UserFactory()
        profile = user.profile
        user.first_name = "Updated"
        user.save()
        profile.refresh_from_db()
        assert not profile.avatar


@pytest.mark.django_db
class TestProfileStr:
    def test_str_representation(self):
        user = UserFactory(username="jean")
        assert str(user.profile) == "Profil de jean"


class TestAvatarValidation:
    def test_rejects_invalid_mime_type(self):
        file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain",
        )
        with pytest.raises(ValidationError) as exc_info:
            validate_avatar(file)
        assert "Format non autorisé" in str(exc_info.value)

    def test_rejects_oversized_file(self):
        data = b"x" * (5 * 1024 * 1024 + 1)
        file = SimpleUploadedFile(
            "large.jpg",
            data,
            content_type="image/jpeg",
        )
        with pytest.raises(ValidationError) as exc_info:
            validate_avatar(file)
        assert "5 Mo" in str(exc_info.value)

    def test_accepts_valid_jpeg(self):
        from io import BytesIO

        from PIL import Image

        buf = BytesIO()
        Image.new("RGB", (10, 10), color="red").save(buf, format="JPEG")
        file = SimpleUploadedFile(
            "photo.jpg",
            buf.getvalue(),
            content_type="image/jpeg",
        )
        validate_avatar(file)

    def test_accepts_valid_png(self):
        from io import BytesIO

        from PIL import Image

        buf = BytesIO()
        Image.new("RGB", (10, 10), color="red").save(buf, format="PNG")
        file = SimpleUploadedFile(
            "photo.png",
            buf.getvalue(),
            content_type="image/png",
        )
        validate_avatar(file)

    def test_accepts_valid_webp(self):
        from io import BytesIO

        from PIL import Image

        buf = BytesIO()
        Image.new("RGB", (10, 10), color="red").save(buf, format="WEBP")
        file = SimpleUploadedFile(
            "photo.webp",
            buf.getvalue(),
            content_type="image/webp",
        )
        validate_avatar(file)

    def test_validate_avatar_handles_missing_file(self):
        from unittest.mock import PropertyMock, patch

        from django.db.models.fields.files import FieldFile

        mock_field_file = FieldFile(None, Profile.avatar.field, "avatars/missing.jpg")
        with patch.object(
            type(mock_field_file), "size", new_callable=PropertyMock, side_effect=FileNotFoundError
        ):
            with pytest.raises(ValidationError) as exc_info:
                validate_avatar(mock_field_file)
            assert "inaccessible" in str(exc_info.value)

    def test_validate_avatar_handles_value_error(self):
        from unittest.mock import PropertyMock, patch

        from django.db.models.fields.files import FieldFile

        mock_field_file = FieldFile(None, Profile.avatar.field, "avatars/broken.jpg")
        with patch.object(
            type(mock_field_file),
            "size",
            new_callable=PropertyMock,
            side_effect=ValueError("no file associated"),
        ):
            with pytest.raises(ValidationError) as exc_info:
                validate_avatar(mock_field_file)
            assert "inaccessible" in str(exc_info.value)

    def test_validate_avatar_skips_empty_fieldfile(self):
        from django.db.models.fields.files import FieldFile

        empty_field_file = FieldFile(None, Profile.avatar.field, "")
        validate_avatar(empty_field_file)

    def test_validate_avatar_skips_none(self):
        validate_avatar(None)

    def test_validate_avatar_checks_mime_on_fieldfile(self):
        from unittest.mock import MagicMock

        mock_file = MagicMock()
        mock_file.size = 1000
        mock_file.content_type = "text/plain"
        mock_file.__bool__ = lambda self: True
        with pytest.raises(ValidationError) as exc_info:
            validate_avatar(mock_file)
        assert "Format non autorisé" in str(exc_info.value)

    def test_rejects_fake_content_type(self):
        """Un fichier .txt avec content_type=image/jpeg doit être rejeté."""
        file = SimpleUploadedFile(
            "fake.jpg",
            b"this is plain text, not an image",
            content_type="image/jpeg",
        )
        with pytest.raises(ValidationError) as exc_info:
            validate_avatar(file)
        assert "Format non autorisé" in str(exc_info.value)

    def test_rejects_file_without_content_type(self):
        """Un fichier sans content_type doit être rejeté."""
        file = SimpleUploadedFile(
            "mystery.bin",
            b"some binary data",
        )
        file.content_type = None
        with pytest.raises(ValidationError) as exc_info:
            validate_avatar(file)
        assert "Format non autorisé" in str(exc_info.value)

    def test_rejects_pdf_file(self):
        """Un fichier PDF doit être rejeté."""
        file = SimpleUploadedFile(
            "document.pdf",
            b"%PDF-1.4 some pdf content here",
            content_type="application/pdf",
        )
        with pytest.raises(ValidationError) as exc_info:
            validate_avatar(file)
        assert "Format non autorisé" in str(exc_info.value)


@pytest.mark.django_db
class TestAvatarCompression:
    def test_avatar_is_compressed_on_save(self):
        """Large image is resized to max 300x300 and compressed."""
        user = UserFactory()
        profile = user.profile
        profile.avatar = _make_image(2000, 1500, "JPEG")
        profile.save()

        img = Image.open(profile.avatar)
        assert img.size[0] <= 300
        assert img.size[1] <= 300
        assert img.format == "JPEG"
        # Compressed file should be much smaller than original
        profile.avatar.seek(0, 2)
        assert profile.avatar.tell() < 100_000

    def test_avatar_png_converted_to_jpeg(self):
        """PNG with transparency is converted to JPEG with white background."""
        user = UserFactory()
        profile = user.profile
        profile.avatar = _make_image(500, 500, "PNG", mode="RGBA")
        profile.save()

        img = Image.open(profile.avatar)
        assert img.format == "JPEG"
        assert profile.avatar.name.endswith(".jpg")

    def test_avatar_not_reprocessed_on_save_without_change(self):
        """Saving profile without changing avatar doesn't reprocess it."""
        user = UserFactory()
        profile = user.profile
        profile.avatar = _make_image(200, 200, "JPEG")
        profile.save()

        profile.avatar.seek(0)
        original_data = profile.avatar.read()

        # Save again without changing avatar
        profile.save()

        profile.avatar.seek(0)
        new_data = profile.avatar.read()
        assert original_data == new_data

    def test_small_avatar_still_processed(self):
        """Even small images are converted to JPEG."""
        user = UserFactory()
        profile = user.profile
        profile.avatar = _make_image(50, 50, "PNG")
        profile.save()

        img = Image.open(profile.avatar)
        assert img.format == "JPEG"
        assert img.size == (50, 50)
