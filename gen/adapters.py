from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import url_str_to_user_pk
from allauth.utils import build_absolute_uri
from django.urls import reverse

from .settings import FRONTEND_DOMAIN


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        key = emailconfirmation.key
        frontend_domain = (
            FRONTEND_DOMAIN if FRONTEND_DOMAIN else "http://localhost:5173"
        )
        return f"{frontend_domain}/verify-email/{key}/"

    def get_password_reset_url(self, request=None, **kwargs):
        # Get the frontend domain from the request or set your default domain here
        print("running...")
        frontend_domain = (
            FRONTEND_DOMAIN if FRONTEND_DOMAIN else "http://localhost:5173"
        )

        # Build the password reset URL
        reset_url = reverse("rest_password_reset")
        # print("reset_url {}".format(reset_url))
        reset_url = build_absolute_uri(request, reset_url)
        # print(f"{reset_url=}")
        user_id = kwargs["user"].pk
        uid = url_str_to_user_pk(str(user_id))
        # print(uid)
        reset_url = f"{frontend_domain}{reset_url}?uid={uid}"
        # print(f"{reset_url=}")
        return reset_url
