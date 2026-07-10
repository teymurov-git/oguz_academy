from django.contrib import admin
from teachers.models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'hire_date', 'is_active')
    list_filter = ('is_active', 'specialization')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'specialization')
    raw_id_fields = ('user',)
