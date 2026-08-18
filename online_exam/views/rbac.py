from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models.rbac import (
    AdminUser, Module, ModuleList, ListField,
    ModulePermission, ListPermission, FieldPermission, PermissionLog,
)
from ..serializers.rbac import (
    AdminUserSerializer, AdminUserListSerializer,
    ModuleSerializer, ModuleListSerializer, ListFieldSerializer,
    ModulePermissionSerializer, ListPermissionSerializer,
    FieldPermissionSerializer, PermissionLogSerializer,
)


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = AdminUser.objects.select_related("user").all()
    filterset_fields = ["is_active"]
    search_fields = ["first_name", "last_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return AdminUserListSerializer
        return AdminUserSerializer

    @action(detail=True, methods=["get"], url_path="permissions")
    def user_permissions(self, request, pk=None):
        """Bu adminin bütün icazələrini qaytarır."""
        admin_user = self.get_object()
        module_perms = ModulePermission.objects.filter(admin_user=admin_user)
        list_perms = ListPermission.objects.filter(admin_user=admin_user)
        field_perms = FieldPermission.objects.filter(admin_user=admin_user)

        return Response({
            "module_permissions": ModulePermissionSerializer(module_perms, many=True).data,
            "list_permissions": ListPermissionSerializer(list_perms, many=True).data,
            "field_permissions": FieldPermissionSerializer(field_perms, many=True).data,
        })


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    ordering_fields = ["order"]


class ModuleListViewSet(viewsets.ModelViewSet):
    queryset = ModuleList.objects.select_related("module").all()
    serializer_class = ModuleListSerializer
    filterset_fields = ["module"]


class ListFieldViewSet(viewsets.ModelViewSet):
    queryset = ListField.objects.select_related("module_list").all()
    serializer_class = ListFieldSerializer
    filterset_fields = ["module_list"]


class ModulePermissionViewSet(viewsets.ModelViewSet):
    queryset = ModulePermission.objects.select_related("admin_user", "module").all()
    serializer_class = ModulePermissionSerializer
    filterset_fields = ["admin_user", "module"]


class ListPermissionViewSet(viewsets.ModelViewSet):
    queryset = ListPermission.objects.select_related("admin_user", "module_list").all()
    serializer_class = ListPermissionSerializer
    filterset_fields = ["admin_user", "module_list"]


class FieldPermissionViewSet(viewsets.ModelViewSet):
    queryset = FieldPermission.objects.select_related("admin_user", "list_field").all()
    serializer_class = FieldPermissionSerializer
    filterset_fields = ["admin_user", "list_field"]


class PermissionLogViewSet(viewsets.ModelViewSet):
    queryset = PermissionLog.objects.select_related("admin_user").all()
    serializer_class = PermissionLogSerializer
    filterset_fields = ["admin_user", "action", "module_name"]
    ordering_fields = ["created_at"]
