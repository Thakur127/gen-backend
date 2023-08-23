from rest_framework import permissions
from .models import Enroll, Course, Lecture
from user.models import RoleChoices


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Allow only user which as a role=Teacher to create a course
    """

    def has_permission(self, request, view):
        print(request.method)
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role == RoleChoices.TEACHER


class IsCourseOwnerOrInstructorsAndEnrolledStudentReadOnly(permissions.BasePermission):

    """
    Course owner can make changes
    in a lecture and instructors & enrolled students can only
    read the lectures
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # Check if the student is enrolled in the course
            course_id = view.kwargs.get("course_id")
            course = Course.objects.filter(pk=course_id).first()
            chapter = view.kwargs.get("chapter")
            if request.method in permissions.SAFE_METHODS:
                return (
                    Enroll.objects.filter(
                        student=request.user, course_id=course_id
                    ).exists()
                    or course.owner == request.user
                    or request.user in course.instructors.all()
                )

            return course.owner == request.user


class IsCourseOwnerOrInstructorsOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        course_id = view.kwargs.get("course_id")

        course = Course.objects.filter(id=course_id).first()
        print(course)

        if course:
            # Check if the requesting user is the owner or a teacher of the course
            return (
                course.owner == request.user or request.user in course.instructors.all()
            )

        return False


class IsEnrolledStudentsOnly(permissions.BasePermission):

    """
    Only Enrolled students in a course can do action
    """

    def has_permission(self, request, view):
        print(request.data)
        course_id = view.kwargs.get("course_id")
        course = Course.objects.filter(pk=course_id).first()

        if request.method in permissions.SAFE_METHODS:
            return True

        if course:
            return request.user in course.enrollments.all()
