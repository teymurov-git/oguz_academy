from django.contrib import admin
from oguz.admin_site import admin_site
from exam_system.models import (
    Exam, Question, Variant, StudentExam,
    StudentAnswer, MarkerConsensus, Competition
)


class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_type', 'status', 'subject', 'total_questions', 'total_time_minutes', 'start_datetime', 'is_active')
    list_filter = ('exam_type', 'status', 'is_active')
    search_fields = ('title', 'subject', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('course', 'group', 'created_by')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'question_type', 'difficulty', 'points', 'sort_order', 'is_active')
    list_filter = ('question_type', 'difficulty', 'is_active')
    search_fields = ('text',)
    raw_id_fields = ('exam',)


class VariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'exam', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    raw_id_fields = ('exam',)
    filter_horizontal = ('questions',)


class StudentExamAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'variant', 'status', 'score', 'percentage', 'passed', 'started_at', 'completed_at')
    list_filter = ('status', 'passed')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'exam__title')
    raw_id_fields = ('exam', 'student', 'variant')


class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student_exam', 'question', 'is_correct', 'points_earned', 'answered_at')
    list_filter = ('is_correct',)
    raw_id_fields = ('student_exam', 'question')


class MarkerConsensusAdmin(admin.ModelAdmin):
    list_display = ('student_answer', 'marker1_score', 'marker2_score', 'marker3_score', 'final_score', 'is_resolved')
    list_filter = ('is_resolved',)
    raw_id_fields = ('student_answer', 'marker1_user', 'marker2_user', 'marker3_user')


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_datetime', 'end_datetime', 'is_active')
    list_filter = ('status', 'is_active')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('exams',)


admin_site.register(Exam, ExamAdmin)
admin_site.register(Question, QuestionAdmin)
admin_site.register(Variant, VariantAdmin)
admin_site.register(StudentExam, StudentExamAdmin)
admin_site.register(StudentAnswer, StudentAnswerAdmin)
admin_site.register(MarkerConsensus, MarkerConsensusAdmin)
admin_site.register(Competition, CompetitionAdmin)
