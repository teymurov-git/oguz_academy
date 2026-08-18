from django.contrib import admin
from homework.models import Homework, HomeworkSubmission
from oguz.admin_site import admin_site


class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'teacher', 'due_date', 'is_active')
    list_filter = ('is_active', 'due_date')
    raw_id_fields = ('lesson', 'group', 'teacher')


class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('homework', 'student', 'status', 'score', 'submitted_at')
    list_filter = ('status',)
    raw_id_fields = ('homework', 'student', 'graded_by')


admin_site.register(Homework, HomeworkAdmin)
admin_site.register(HomeworkSubmission, HomeworkSubmissionAdmin)