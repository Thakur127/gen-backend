from django.db import models
from user.models import CustomUser as User
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from moneyed import list_all_currencies, get_country_name


class AvailableCurrency(models.TextChoices):
    USD = "USD", _("United States Dollar")
    INR = "INR", _("Indian Rupee")
    EUR = "EUR", _("EURO")
    RUB = "RUB", _("Russian Ruble")
    JPY = "JPY", _("Japanese Yen")
    AUD = "AUD", _("Australian Dollar")
    CNY = "CNY", _("Chinese Yuan")
    GBP = "GBP", _("British Pound Sterling")


class CourseCategory(models.TextChoices):
    MATHEMATICS = "MA", _("Mathematics")
    PHYSICS = "PH", _("Physics")
    ECONOMICS = "EC", _("Economics")
    FINANCE_MARKETING = "FM", _("Finance & Marketing")
    COMPUTER_SCIENCE = "CS", _("Computer Science")
    NOT_CATEGORIZED = "NC", _("Not Categorized")


class Course(models.Model):
    title = models.CharField(max_length=64, verbose_name="Course Title")
    category = models.CharField(
        choices=CourseCategory.choices,
        default=CourseCategory.NOT_CATEGORIZED,
        max_length=32,
    )
    description = models.CharField(max_length=128)
    outcomes = models.TextField(verbose_name="Outcome of the Course")
    prerequisites = models.TextField(
        blank=True, verbose_name="Prerequisites for the course"
    )
    price = models.DecimalField(
        verbose_name="Course Price",
        max_digits=7,
        decimal_places=2,
    )
    currency = models.CharField(
        max_length=3,
        choices=AvailableCurrency.choices,
        default=AvailableCurrency.INR,
    )
    cover_img = models.URLField(
        max_length=256,
    )
    preview_video = models.URLField(blank=True, max_length=256)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    languages = models.CharField(max_length=108)
    captions = models.CharField(blank=True, max_length=108)
    instructors = models.ManyToManyField(
        User, related_name="course_instructors", blank=True
    )
    enrollments = models.ManyToManyField(
        User, related_name="enrolled_students", blank=True
    )
    rating = models.FloatField(blank=True, default=0)
    totalRatings = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Lecture(models.Model):
    title = models.CharField(max_length=64, verbose_name="Lecture Title")
    description = models.CharField(
        max_length=256, blank=True, verbose_name="Lecture Description"
    )
    lecture_url = models.URLField(verbose_name="Lecture Url")
    thumbnail = models.URLField(blank=True, verbose_name="Cover Image")
    duration = models.DurationField(default=timedelta(hours=0, minutes=0, seconds=0))
    chapter = models.IntegerField(
        help_text="Chapter no. or position in a course. May help to set order of the lectures."
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lectures"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Enroll(models.Model):
    enrollment_no = models.CharField(max_length=12, unique=True, blank=True)
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrolled_student"
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name="enrollment_course"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.enrollment_no:
            # Generate a random six-digit number
            enrollment_no = get_random_string(length=10, allowed_chars="1234567890")

            # Check if the generated number is unique
            while Enroll.objects.filter(enrollment_no=enrollment_no).exists():
                enrollment_no = get_random_string(length=6, allowed_chars="1234567890")

            self.enrollment_no = enrollment_no

        super().save(*args, **kwargs)

    def __str__(self):
        return self.enrollment_no


class Discussion(models.Model):
    discussion = models.CharField(max_length=100, blank=True)
    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="discussion_lecture"
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="discussion_student"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.discussion


class Review(models.Model):
    review = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="reviewed_course"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


from .signals import add_student_to_course_enrollments, remove_enrollment_from_course
