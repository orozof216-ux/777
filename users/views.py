import random
import string

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .models import ConfirmationCode, CustomUser
from .serializers import (
    AuthValidateSerializer,
    ConfirmationSerializer,
    RegisterValidateSerializer,
)


class AuthorizationAPIView(CreateAPIView):
    serializer_class = AuthValidateSerializer

    def post(self, request):
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        if user:
            if not user.is_active:
                return Response(
                    {"error": "User account is not activated yet!"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            token, _ = Token.objects.get_or_create(user=user)
            return Response({"key": token.key})

        return Response(
            {"error": "User credentials are wrong!"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        phone_number = serializer.validated_data.get("phone_number")

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                phone_number=phone_number,
                is_active=False,
            )

            code = "".join(random.choices(string.digits, k=6))

            ConfirmationCode.objects.create(
                user=user,
                code=code,
            )

        return Response(
            {
                "user_id": user.id,
                "confirmation_code": code,
            },
            status=status.HTTP_201_CREATED,
        )


class ConfirmUserAPIView(CreateAPIView):
    serializer_class = ConfirmationSerializer

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

            ConfirmationCode.objects.filter(user=user).delete()

        return Response(
            {
                "message": "User аккаунт успешно активирован",
                "key": token.key,
            },
            status=status.HTTP_200_OK,
        )