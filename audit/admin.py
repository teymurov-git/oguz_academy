from django.contrib import admin
from audit.models import AuditLog
from oguz.admin_site import admin_site


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'module', 'model_name', 'object_repr', 'created_at')
    list_filter = ('action', 'module', 'created_at')
    search_fields = ('object_repr', 'module')
    raw_id_fields = ('user',)
    readonly_fields = ('user', 'action', 'module', 'model_name', 'object_id', 'object_repr', 'details', 'ip_address', 'user_agent', 'created_at')


admin_site.register(AuditLog, AuditLogAdmin)