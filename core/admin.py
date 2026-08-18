from django.contrib import admin
from core.models import Contact, Subscriber
from oguz.admin_site import admin_site


class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('email',)
    readonly_fields = ('created_at', 'updated_at')


admin_site.register(Contact, ContactAdmin)
admin_site.register(Subscriber, SubscriberAdmin)