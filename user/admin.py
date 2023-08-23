from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "pk",
        "email",
        "role",
        "is_active",
    )
    list_display_links = ("pk", "email")
    list_filter = (
        "email",
        "username",
        "role",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (
            "Info",
            {
                "fields": (
                    "password",
                    "email",
                    "verified_email",
                    "username",
                    "first_name",
                    "last_name",
                    "image_url",
                    "role",
                    "last_login",
                    "date_joined",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "role",
                ),
            },
        ),
    )
    search_fields = ("email", "username")
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
