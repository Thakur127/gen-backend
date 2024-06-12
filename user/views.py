from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from rest_framework import generics, status
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from dj_rest_auth.serializers import (
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView
from django.core.mail import send_mail
from django.conf import settings

from .serializers import CustomUserDetailsSerializer
from gen.permissions import IsOwnerOrReadOnly

User = get_user_model()
FRONTEND_DOMAIN = settings.FRONTEND_DOMAIN


class CustomPasswordResetView(PasswordResetView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if "allauth" in settings.INSTALLED_APPS:
            from allauth.account.utils import user_pk_to_url_str as uid_encoder
            from allauth.account.forms import default_token_generator
        else:
            from django.utils.http import urlsafe_base64_encode as uid_encoder
            from django.contrib.auth.tokens import default_token_generator

        if user:
            if not user.pk:
                return Response(
                    {"detail": "Invalid user ID. Cannot reset password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Generate a password reset token
            token_generator = default_token_generator
            if "allauth" in settings.INSTALLED_APPS:
                uid = uid_encoder(user)
            else:
                uid = uid_encoder(force_bytes(str(user.pk)))
            token = token_generator.make_token(user)

            print(uid, token)
            # Build the password reset URL
            frontend_domain = (
                FRONTEND_DOMAIN if FRONTEND_DOMAIN else "http://localhost:5173"
            )
            reset_url = f"{frontend_domain}/password-reset/{uid}/{token}/"

            # Send the password reset email
            context = {
                "user": user,
                "reset_url": reset_url,
                "site_name": get_current_site(request).name,
                "domain": frontend_domain,
            }

            email_template_name = "account/email/password_reset_email.html"
            subject = "Password Reset Request"
            email_body = render_to_string(email_template_name, context)

            send_mail(subject, "", None, [email], html_message=email_body)

            return Response(
                {"detail": "Password reset e-mail has been sent."},
                status=status.HTTP_200_OK,
            )

        return Response({"error": "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = CustomUserDetailsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    lookup_field = "username"
