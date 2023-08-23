from django.urls import path
from . import views

urlpatterns = [
    path("courses/", views.CourseListView.as_view(), name="course-list"),
    path(
        "user/<str:username>/courses/",
        views.UserCourseListView.as_view(),
        name="my-courses",
    ),
    path("course/<int:pk>/", views.CourseDetailView.as_view()),
    path(
        "course/<int:course_id>/lectures/",
        views.LectureListView.as_view(),
        name="lecture-list",
    ),
    path(
        "course/<int:course_id>/lecture/<int:chapter>/",
        views.LectureDetailView.as_view(),
    ),
    path("course/enroll/", views.EnrollListView.as_view(), name="enroll"),
    path(
        "course/<int:course_id>/reviews/",
        views.ReviewListView.as_view(),
        name="reviews",
    ),
    path(
        "course/review/<int:pk>/",
        views.ReviewDetailView.as_view(),
        name="review_detail",
    ),
    path(
        "course/<int:course_id>/lecture/<int:chapter>/discussions/",
        views.DiscussionListView.as_view(),
        name="discussion",
    ),
]
