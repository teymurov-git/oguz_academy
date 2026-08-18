from django.contrib import admin
from oguz.admin_site import admin_site
from system_settings.models import SystemSetting


class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_public', 'updated_at')
    list_filter = ('is_public',)
    search_fields = ('key', 'description')


admin_site.register(SystemSetting, SystemSettingAdmin)
