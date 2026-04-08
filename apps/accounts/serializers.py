import random

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("avatar",)


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "avatar", "is_superuser")
        read_only_fields = ("id", "username", "email", "is_superuser")

    def get_avatar(self, obj):
        if hasattr(obj, "profile") and obj.profile.avatar:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile.avatar.url)
            return obj.profile.avatar.url
        return None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Adresse email ou mot de passe incorrect."
            )

        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError(
                "Adresse email ou mot de passe incorrect."
            )

        data["user"] = user
        return data


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Un compte avec cet email existe déjà."
            )
        return value

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError(
                {"password2": "Les mots de passe ne correspondent pas."}
            )
        try:
            validate_password(data["password1"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password1": list(e.messages)})
        return data

    def create(self, validated_data):
        email = validated_data["email"]
        local_part = email.split("@")[0]
        username = local_part
        while User.objects.filter(username=username).exists():
            username = f"{local_part}_{random.randint(1000, 9999)}"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data["password1"],
        )
        return user
