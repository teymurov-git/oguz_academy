from rest_framework import serializers
from roles.models import Role, Permission, RolePermission, UserRole


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_permissions(self, obj):
        return [rp.permission.codename for rp in obj.role_permissions.all()]


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'
