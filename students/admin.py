from django.contrib import admin
from students.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'enrollment_date', 'is_active')
    list_filter = ('is_active', 'enrollment_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone')
    raw_id_fields = ('user',)
