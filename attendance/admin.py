from django.contrib import admin
from attendance.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name')
    raw_id_fields = ('student', 'group')
    date_hierarchy = 'date'
