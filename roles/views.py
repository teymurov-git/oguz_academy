from rest_framework import viewsets
from roles.models import Role, Permission, UserRole
from roles.serializers import RoleSerializer, PermissionSerializer, UserRoleSerializer
from rest_framework.permissions import IsAdminUser


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    search_fields = ('name',)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]
    search_fields = ('codename', 'name', 'module')


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdminUser]
