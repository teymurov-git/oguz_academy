from rest_framework import serializers
from ..models import (
    CourseEnrollment, CourseTeacherSchedule, CoursePaymentRecord,
)


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = "__all__"


class CourseTeacherScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTeacherSchedule
        fields = "__all__"


class CoursePaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePaymentRecord
        fields = "__all__"
