from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Enroll


@receiver(post_save, sender=Enroll)
def add_student_to_course_enrollments(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        student = instance.student
        course.enrollments.add(student)


@receiver(pre_delete, sender=Enroll)
def remove_enrollment_from_course(sender, instance, **kwargs):
    # Remove the enrollment from enrollments field of the associated course
    instance.course.enrollments.remove(instance.student)

