from .models import Enroll, User, Course
from .serializers import EnrollmentNumberSerializer


def user_enrollment(user: User, course: Course) -> Enroll:
    """
    Returns enrollment objects if exists

    Args:
        user (User): Accepts user object
        course (Course): Accepts course object

    Returns:
        Enroll: enrollment of user into a course
    """

    try:
        enrollment = Enroll.objects.filter(student=user, course=course).first()
        if enrollment:
            serializer = EnrollmentNumberSerializer(enrollment)
            return serializer.data
    except Exception as e:
        print(e)
        return None
