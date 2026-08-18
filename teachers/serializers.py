from rest_framework import serializers
from teachers.models import Teacher
from account.serializers import UserSerializer


class TeacherListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ('id', 'teacher_id', 'full_name', 'specialization', 'phone', 'hourly_rate', 'is_active')

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class TeacherDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = '__all__'
