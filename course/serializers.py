from rest_framework import serializers

from .models import Course, Lecture, Enroll, Discussion, Review
from user.serializers import CustomUserDetailsSerializer


class LectureSerializer(serializers.ModelSerializer):
    # course = serializers.ReadOnlyField()
    course = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Lecture
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    owner = CustomUserDetailsSerializer(read_only=True)
    lectures = LectureSerializer(many=True, read_only=True)
    instructors = CustomUserDetailsSerializer(read_only=True, many=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Course
        fields = "__all__"

    def get_category_display(self, obj):
        return obj.get_category_display()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"] = instance.get_category_display()
        return data


class EnrollSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enroll
        fields = ("enrollment_no", "course", "enrolled_at")

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data["student"] = data["student"][
    #         "email"
    #     ]  # Display only the email of the student
    #     data["course"] = data["course"]["title"]  # Display only the title of the course
    #     return data


class EnrollmentNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enroll
        fields = ("enrollment_no", "enrolled_at")


class DiscussionSerializer(serializers.ModelSerializer):
    student = CustomUserDetailsSerializer(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Discussion
        fields = ("discussion", "student", "updated_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["student"] = data["student"]["username"]
        return data


class ReviewSerializer(serializers.ModelSerializer):
    owner = CustomUserDetailsSerializer(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
