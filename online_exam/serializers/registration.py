from rest_framework import serializers
from ..models import Register


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = "__all__"


class RegisterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = [
            "id", "first_name", "last_name", "father_name", "phone", "gender",
            "student_reg_number", "student_class", "student_section",
            "student_group", "exam_id", "student_total_price", "student_payment",
            "is_paid", "payment_status", "payment_method", "has_incomplete_data",
            "created_at",
        ]
