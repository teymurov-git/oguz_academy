from django.contrib import admin
from roles.models import Role, Permission, RolePermission, UserRole
from oguz.admin_site import admin_site


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    autocomplete_fields = ('permission',)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_system', 'permission_count', 'user_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    list_filter = ('is_system',)
    inlines = [RolePermissionInline]

    def permission_count(self, obj):
        return obj.role_permissions.count()
    permission_count.short_description = 'İcazə sayı'

    def user_count(self, obj):
        return obj.user_roles.count()
    user_count.short_description = 'İstifadəçi sayı'


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'name', 'module', 'action', 'role_count')
    list_filter = ('module', 'action')
    search_fields = ('codename', 'name', 'module')

    def role_count(self, obj):
        return obj.role_permissions.count()
    role_count.short_description = 'Rol sayı'


class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission', 'module')
    list_filter = ('role', 'permission__module')
    raw_id_fields = ('role', 'permission')

    def module(self, obj):
        return obj.permission.module
    module.short_description = 'Modul'


class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    raw_id_fields = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'role__name')


admin_site.register(Role, RoleAdmin)
admin_site.register(Permission, PermissionAdmin)
admin_site.register(RolePermission, RolePermissionAdmin)
admin_site.register(UserRole, UserRoleAdmin)