import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import Profile, validate_avatar

from .factories import UserFactory

User = get_user_model()


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
        original_avatar = profile.avatar.name
        user.first_name = "Updated"
        user.save()
        profile.refresh_from_db()
        assert profile.avatar.name == original_avatar


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
        file = SimpleUploadedFile(
            "photo.jpg",
            b"\xff\xd8\xff" + b"x" * 100,
            content_type="image/jpeg",
        )
        validate_avatar(file)

    def test_accepts_valid_png(self):
        file = SimpleUploadedFile(
            "photo.png",
            b"\x89PNG" + b"x" * 100,
            content_type="image/png",
        )
        validate_avatar(file)

    def test_accepts_valid_webp(self):
        file = SimpleUploadedFile(
            "photo.webp",
            b"RIFF" + b"x" * 100,
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
