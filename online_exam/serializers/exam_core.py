from rest_framework import serializers
from ..models import Exam, CorrectAnswerKey, ExamSessions


class ExamSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.CharField(source="exam_type.exam_type_name", read_only=True, default="")

    class Meta:
        model = Exam
        fields = "__all__"


class ExamListSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.CharField(source="exam_type.exam_type_name", read_only=True, default="")

    class Meta:
        model = Exam
        fields = [
            "exam_id", "exam_name", "exam_date", "exam_image", "exam_type",
            "exam_type_name", "exam_register", "exam_result", "does_answers_added",
            "exam_register_count", "payment_type", "created_at",
        ]


class CorrectAnswerKeySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.subject_name", read_only=True, default="")

    class Meta:
        model = CorrectAnswerKey
        fields = "__all__"


class ExamSessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSessions
        fields = "__all__"
