from django.contrib import admin
from django.urls import path, include, re_path
from dj_rest_auth.registration.views import ConfirmEmailView, VerifyEmailView
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # User Authentication
    path("api/auth/", include("user.urls")),
    # Course
    path("api/", include("course.urls")),
    # Payments
    path("api/payments/", include("payments.urls")),
]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
