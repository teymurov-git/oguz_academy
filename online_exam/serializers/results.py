from rest_framework import serializers
from ..models import SagirdResult


class SagirdResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SagirdResult
        fields = "__all__"


class SagirdResultListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SagirdResult
        fields = [
            "id", "student_id", "exam_id", "student_reg_number",
            "first_name", "last_name", "sinif", "variant",
            "bolme", "qrup", "total_point", "attempt_number", "created_at",
        ]
