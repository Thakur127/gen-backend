from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

# Create your models here.


class RoleChoices(models.TextChoices):
    STUDENT = "ST", _("Student")
    TEACHER = "TR", _("Teacher")


class CustomUser(AbstractUser):
    username = models.CharField(blank=True, max_length=16)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(blank=True, max_length=64)
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        max_length=2, choices=RoleChoices.choices, default=RoleChoices.STUDENT
    )
    verified_email = models.BooleanField(default=False)
    image_url = models.URLField(blank=True)
    bio = models.CharField(blank=True, max_length=108)
    qualifications = models.CharField(blank=True, max_length=108)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role", "first_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Check if the username is empty or not provided
        if not self.username:
            # Create a username using the first_name and last_name
            if self.first_name and self.last_name:
                username = f"{self.first_name.lower()}.{self.last_name.lower()}"
            else:
                username = self.email.split("@")[0]

            # Check if the generated username is unique
            i = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{username}{i}"
                i += 1

            self.username = username

        super().save(*args, **kwargs)
