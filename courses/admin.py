from django.contrib import admin
from courses.models import Exam, ExamRegistration, Course, Group


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'registration_deadline', 'is_active')
    list_filter = ('is_active', 'date')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ExamRegistration)
class ExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'exam', 'registered_at')
    list_filter = ('exam', 'registered_at')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_weeks', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'teacher', 'start_date', 'max_students', 'is_active')
    list_filter = ('is_active', 'course', 'start_date')
    search_fields = ('name', 'course__name')
    filter_horizontal = ('students',)
    raw_id_fields = ('teacher',)
