from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status


from gen.permissions import IsOwnerOrReadOnly, IsOwnerOnly
from .permissions import (
    IsTeacherOrReadOnly,
    IsCourseOwnerOrInstructorsOnly,
    IsCourseOwnerOrInstructorsAndEnrolledStudentReadOnly,
    IsEnrolledStudentsOnly,
)
from .serializers import (
    CourseSerializer,
    LectureSerializer,
    EnrollSerializer,
    DiscussionSerializer,
    ReviewSerializer,
)
from .models import Course, Lecture, Enroll, Discussion, Review
from user.models import CustomUser as User
from rest_framework.pagination import CursorPagination


class MyCursorPagination(CursorPagination):
    page_size = 4
    ordering = "enrollments"


class CourseListView(ListCreateAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [IsTeacherOrReadOnly]
    pagination_class = MyCursorPagination

    def get_queryset(self):
        # filter course acc. to category
        category = self.request.query_params.get("category")
        if category:
            return Course.objects.filter(category__icontains=category)

        # search course title
        q = self.request.query_params.get("q")
        if q:
            return Course.objects.filter(title__icontains=q)

        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsOwnerOrReadOnly]


class UserCourseListView(ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsOwnerOnly]

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        return Course.objects.filter(owner=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        username = self.kwargs.get("username")
        if queryset is None:
            return Response(
                data={"detail": f"User doesn't exist with the username '{username}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif not queryset:
            return Response(
                data={
                    "detail": "Didn't find any course with the username '{username}'."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LectureListView(ListCreateAPIView):
    serializer_class = LectureSerializer
    permission_classes = [IsCourseOwnerOrInstructorsOnly]

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        return Lecture.objects.filter(course_id=course_id)

    def create(self, request, *args, **kwargs):
        course_id = self.kwargs.get("course_id")
        chapter = request.data.get("chapter")

        try:
            if int(chapter) < 0:
                return Response(
                    {"error": "Chapter no. should be positive"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Lecture.objects.filter(course=course_id, chapter=chapter).exists():
                return Response(
                    {
                        "error": "You can't have two letures with same chapter no. in a single course."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return super().create(request, *args, **kwargs)
        except Lecture.DoesNotExist:
            pass

    def perform_create(self, serializer):
        course_id = self.kwargs.get("course_id")
        try:
            course = Course.objects.get(pk=course_id)
            serializer.save(course=course)
        except Course.DoesNotExist:
            return Response(
                {"error": f"No Course Associated with id {course_id}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LectureDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LectureSerializer
    permission_classes = [
        IsCourseOwnerOrInstructorsAndEnrolledStudentReadOnly,
    ]

    def get_object(self):
        chapter = self.kwargs.get("chapter")
        course_id = self.kwargs.get("course_id")
        return Lecture.objects.filter(course=course_id, chapter=chapter).first()


class EnrollListView(ListCreateAPIView):
    serializer_class = EnrollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enroll.objects.filter(student=self.request.user)

    def create(self, request, *args, **kwargs):
        pk = request.data.get("course")
        try:
            course = Course.objects.get(pk=pk)
            if Enroll.objects.get(student=self.request.user, course=course):
                return Response(
                    {"error": "Already Enrolled in this course."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Course.DoesNotExist:
            return Response(
                {"error": f"No course is associated with id {pk}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Enroll.DoesNotExist:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        pk = self.request.data.get("course")
        course = Course.objects.get(pk=pk)
        serializer.save(student=self.request.user, course=course)


class DiscussionListView(ListCreateAPIView):
    serializer_class = DiscussionSerializer
    queryset = Discussion.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        chapter = self.kwargs.get("chapter")
        lecture = Lecture.objects.filter(course_id=course_id, chapter=chapter).first()
        return Discussion.objects.filter(lecture=lecture)

    def perform_create(self, serializer):
        course_id = self.kwargs.get("course_id")
        chapter = self.kwargs.get("chapter")
        lecture = Lecture.objects.filter(course_id=course_id, chapter=chapter).first()
        if lecture:
            serializer.save(lecture=lecture, student=self.request.user)

        return Response(
            data={"error": "No data found with provided info."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ReviewListView(ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsEnrolledStudentsOnly]

    def get_queryset(self):
        course = self.kwargs.get("course_id")
        return Review.objects.filter(course=course).order_by("-created_at")

    def perform_create(self, serializer):
        course_id = self.kwargs.get("course_id")
        try:
            course = Course.objects.get(pk=course_id)
            serializer.save(course=course, owner=self.request.user)
        except Course.DoesNotExist:
            return Response(
                {"error": f"No Course Associated with id {course_id}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOnly]
    queryset = Review.objects.all()
