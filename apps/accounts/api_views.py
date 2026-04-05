from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ProfileForm, UserForm
from .serializers import LoginSerializer, SignupSerializer, UserSerializer


class CSRFTokenAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response(
            UserSerializer(user, context={"request": request}).data
        )


class SignupAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response(
                UserSerializer(request.user, context={"request": request}).data
            )
        return Response({"id": None})


class ProfileUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        user_form = UserForm(request.data, instance=request.user)
        profile_form = ProfileForm(
            request.data, request.FILES, instance=request.user.profile
        )

        errors = {}
        if not user_form.is_valid():
            errors.update(user_form.errors)
        if not profile_form.is_valid():
            errors.update(profile_form.errors)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        user_form.save()
        try:
            profile_form.save()
        except (OSError, AttributeError):
            return Response(
                {"avatar": ["Impossible d'enregistrer l'avatar."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            UserSerializer(request.user, context={"request": request}).data
        )


class AvatarDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = ""
            profile.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
