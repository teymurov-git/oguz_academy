from rest_framework import viewsets

from ..models.course_enrollment import (
    CourseEnrollment, CourseTeacherSchedule, CoursePaymentRecord,
)
from ..serializers.course_enrollment import (
    CourseEnrollmentSerializer, CourseTeacherScheduleSerializer,
    CoursePaymentRecordSerializer,
)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = CourseEnrollment.objects.select_related("student").all()
    serializer_class = CourseEnrollmentSerializer
    filterset_fields = ["payment_type", "is_active"]


class CourseTeacherScheduleViewSet(viewsets.ModelViewSet):
    queryset = CourseTeacherSchedule.objects.select_related("teacher").all()
    serializer_class = CourseTeacherScheduleSerializer
    filterset_fields = []


class CoursePaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = CoursePaymentRecord.objects.select_related("enrollment").all()
    serializer_class = CoursePaymentRecordSerializer
    filterset_fields = ["enrollment"]
