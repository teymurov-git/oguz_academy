from rest_framework import serializers
from ..models import (
    StudentCabinet, ExamParticipation, ExamAttempt,
    OnlineExamAssignment, StudentExamSession, StudentAnswer,
)


class StudentCabinetSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    email = serializers.CharField(source="user.email", read_only=True, default="")

    class Meta:
        model = StudentCabinet
        fields = "__all__"

    def get_user_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else ""


class StudentCabinetListSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    email = serializers.CharField(source="user.email", read_only=True, default="")

    class Meta:
        model = StudentCabinet
        fields = [
            "id", "user", "user_full_name", "email", "work_number",
            "phone", "is_course_student", "student_verification_status",
            "is_active", "created_at",
        ]

    def get_user_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else ""


class ExamParticipationSerializer(serializers.ModelSerializer):
    exam_name_display = serializers.CharField(source="exam.exam_name", read_only=True, default="")

    class Meta:
        model = ExamParticipation
        fields = "__all__"


class ExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = "__all__"


class OnlineExamAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineExamAssignment
        fields = "__all__"


class StudentExamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamSession
        fields = "__all__"


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = "__all__"
