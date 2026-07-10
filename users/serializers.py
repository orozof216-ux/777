from django.core.cache import cache
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


class OAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["email"] = user.email
        token["is_active"] = user.is_active
        token["is_staff"] = user.is_staff

        token["birthdate"] = (
            user.birthdate.strftime("%Y-%m-%d")
            if user.birthdate
            else None
        )

        token["first_name"] = user.first_name
        token["last_name"] = user.last_name

        return token


class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )

    last_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )

    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )

    birthdate = serializers.DateField(
        required=False,
        allow_null=True,
    )


class AuthValidateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegisterValidateSerializer(UserBaseSerializer):
    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Пользователь уже существует!")
        return email


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        code = attrs.get("code")

        try:
            CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("Пользователь не существует!")

        redis_code = cache.get(f"confirmation_code_{user_id}")

        if redis_code is None:
            raise ValidationError("Код подтверждения не найден или истек!")

        if redis_code != code:
            raise ValidationError("Неверный код подтверждения!")

        return attrs