from django.db import models
from django.utils.translation import gettext_lazy as _
from course.models import Enroll, Course, AvailableCurrency
from django.contrib.auth import get_user_model

User = get_user_model()


class Payment(models.Model):
    transaction_id = models.CharField(max_length=108)
    session_id = models.CharField(max_length=108)
    currency = models.CharField(
        max_length=3, choices=AvailableCurrency.choices, default=AvailableCurrency.INR
    )
    payment_status = models.CharField(max_length=18)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    enrollment = models.ForeignKey(
        Enroll, on_delete=models.CASCADE, related_name="payment_enrollment", blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payment_user",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.DO_NOTHING,
        related_name="payment_course",
    )

    def __str__(self):
        return self.transaction_id
