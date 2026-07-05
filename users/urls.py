from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from users.views import (
    RegistrationAPIView,
    AuthorizationAPIView,
    ConfirmUserAPIView,
)
from users.google_oauth import GoogleLoginAPIView

urlpatterns = [
    path("registration/", RegistrationAPIView.as_view(), name="registration"),
    path("authorization/", AuthorizationAPIView.as_view(), name="authorization"),
    path("confirm/", ConfirmUserAPIView.as_view(), name="confirm"),

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    path("google-login/", GoogleLoginAPIView.as_view(), name="google_login"),
]