from rest_framework import serializers
from ..models import (
    AdminUser, Module, ModuleList, ListField,
    ModulePermission, ListPermission, FieldPermission, PermissionLog,
)


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = "__all__"


class AdminUserListSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True, default="")

    class Meta:
        model = AdminUser
        fields = [
            "id", "user", "user_email", "first_name", "last_name",
            "phone", "position", "is_active", "created_at",
        ]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"


class ModuleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleList
        fields = "__all__"


class ListFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListField
        fields = "__all__"


class ModulePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModulePermission
        fields = "__all__"


class ListPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListPermission
        fields = "__all__"


class FieldPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldPermission
        fields = "__all__"


class PermissionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionLog
        fields = "__all__"
