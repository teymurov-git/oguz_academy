from rest_framework import serializers
from students.models import Student, Parent
from account.serializers import UserSerializer


class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Parent
        fields = '__all__'


class StudentListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Student
        fields = ('id', 'student_id', 'full_name', 'email', 'phone', 'status', 'enrollment_date', 'is_active', 'monthly_payment', 'discount', 'payment_status')

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class StudentDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    parent = ParentSerializer(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
