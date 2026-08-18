from django.contrib import admin
from attendance.models import Attendance
from oguz.admin_site import admin_site


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'lesson_date', 'lesson_number', 'status', 'late_minutes', 'marked_by')
    list_filter = ('status', 'lesson_date', 'group')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'student__student_id')
    raw_id_fields = ('student', 'group', 'marked_by')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Davamiyyət', {'fields': ('student', 'group', 'lesson_date', 'lesson_number', 'status', 'late_minutes', 'reason')}),
        ('Əlavə', {'fields': ('marked_by', 'created_at', 'updated_at')}),
    )

    def _is_teacher(self, user):
        return not user.is_superuser and hasattr(user, 'teacher_profile')

    def has_view_permission(self, request, obj=None):
        if self._is_teacher(request.user):
            return True
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if self._is_teacher(request.user):
            return True
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if self._is_teacher(request.user):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self._is_teacher(request.user):
            return False
        return super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self._is_teacher(request.user):
            qs = qs.filter(group__teacher=request.user.teacher_profile)
        return qs


admin_site.register(Attendance, AttendanceAdmin)