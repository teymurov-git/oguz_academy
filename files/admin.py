from django.contrib import admin
from files.models import File
from oguz.admin_site import admin_site


class FileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'module', 'mime_type', 'file_size', 'uploaded_by', 'created_at')
    list_filter = ('module', 'created_at')
    search_fields = ('original_filename',)
    raw_id_fields = ('uploaded_by',)


admin_site.register(File, FileAdmin)