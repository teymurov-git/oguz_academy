from rest_framework import serializers
from payments.models import Payment, PaymentPlan


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class PaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = '__all__'
