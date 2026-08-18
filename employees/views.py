from rest_framework import viewsets
from rest_framework import serializers
from employees.models import Employee, Position


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    search_fields = ('name',)


class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    position_name = serializers.CharField(source='position_fk.name', read_only=True, allow_null=True)

    class Meta:
        model = Employee
        fields = ('id', 'employee_id', 'full_name', 'department', 'position_fk', 'position_name', 'salary', 'salary_type', 'is_active')

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class EmployeeDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    position_name = serializers.CharField(source='position_fk.name', read_only=True, allow_null=True)

    class Meta:
        model = Employee
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'position_fk').all()
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id')

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeDetailSerializer
