from django.contrib import admin
from schedule.models import Schedule, Lesson, LessonAttendance
from oguz.admin_site import admin_site


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('group', 'teacher', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week',)
    raw_id_fields = ('group', 'teacher')


class LessonAdmin(admin.ModelAdmin):
    list_display = ('group', 'lesson_number', 'date', 'start_time', 'topic', 'status')
    list_filter = ('status', 'date', 'group')
    raw_id_fields = ('group', 'schedule', 'teacher')


class LessonAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'status', 'late_minutes', 'points')
    list_filter = ('status',)
    raw_id_fields = ('lesson', 'student')


admin_site.register(Schedule, ScheduleAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(LessonAttendance, LessonAttendanceAdmin)
