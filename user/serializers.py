from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import CustomUser, RoleChoices


class CustomUserRegisterSerializer(RegisterSerializer):
    role = serializers.ChoiceField(
        choices=RoleChoices.choices, default=RoleChoices.STUDENT
    )
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict["role"] = self.validated_data.get("role", None)
        data_dict["first_name"] = self.validated_data.get("first_name", "")
        data_dict["last_name"] = self.validated_data.get("last_name", "")
        return data_dict

    def custom_signup(self, request, user):
        user.role = self.cleaned_data.get("role")
        user.save()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta:
        model = CustomUser
        exclude = (
            "password",
            "user_permissions",
            "groups",
            "is_superuser",
            "is_staff",
            "verified_email",
        )

    def get_role_display(self, obj):
        return obj.get_role_display()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["role"] = instance.get_role_display()
        return data
