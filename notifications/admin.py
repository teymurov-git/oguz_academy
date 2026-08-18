from django.contrib import admin
from notifications.models import Notification, NotificationTemplate
from oguz.admin_site import admin_site


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    raw_id_fields = ('recipient',)


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('key', 'notification_type')


admin_site.register(Notification, NotificationAdmin)
admin_site.register(NotificationTemplate, NotificationTemplateAdmin)