from .models import Payment
from rest_framework import serializers
from course.serializers import CourseSerializer, EnrollSerializer
from user.serializers import UserDetailsSerializer


class PaymentSerializer(serializers.ModelSerializer):
    user = UserDetailsSerializer(read_only=True)
    enrollment = EnrollSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
