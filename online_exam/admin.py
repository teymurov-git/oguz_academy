from django.contrib import admin
from oguz.admin_site import admin_site
from .models import (
    ExamType, Subject, Sinif, Bolme, Qrup, District, SchoolType, School,
    Universities, PreviousExam,
)
from .models import Exam, CorrectAnswerKey, ExamSessions
from .models import Register
from .models import (
    StudentCabinet, ExamParticipation, ExamAttempt,
    OnlineExamAssignment, StudentExamSession, StudentAnswer,
)
from .models import SagirdResult
from .models import (
    Marker, QuestionAssignment, StudentAnswerGrading,
    IndividualGrade, MarkerAnswerGrade,
)
from .models import (
    AdminUser, Module, ModuleList, ListField,
    ModulePermission, ListPermission, FieldPermission, PermissionLog,
)
from .models import (
    Competition, CompetitionQuestion, CompetitionParticipant,
    CompetitionQuestionAttempt,
)
from .models import (
    NotificationTemplate, CabinetNotification, CabinetActivity,
    LoginAttempt, LoginBlock, PasswordResetOTP, WhatsAppTemplate,
    ExamRecording,
)
from .models import (
    CourseEnrollment, CourseTeacherSchedule, CoursePaymentRecord,
)


class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "exam_type_name"]
    search_fields = ["exam_type_name"]


class SubjectAdmin(admin.ModelAdmin):
    list_display = ["id", "subject_name"]
    search_fields = ["subject_name"]


class SinifAdmin(admin.ModelAdmin):
    list_display = ["id", "sinif_name"]


class BolmeAdmin(admin.ModelAdmin):
    list_display = ["id", "bolme_name"]


class QrupAdmin(admin.ModelAdmin):
    list_display = ["id", "qrup_name"]


class DistrictAdmin(admin.ModelAdmin):
    list_display = ["id", "district_name"]
    search_fields = ["district_name"]


class SchoolTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "school_type_name"]


class SchoolAdmin(admin.ModelAdmin):
    list_display = ["id", "school_name", "district", "school_type"]
    search_fields = ["school_name"]
    list_filter = ["district", "school_type"]


class UniversitiesAdmin(admin.ModelAdmin):
    list_display = ["id", "university_name"]
    search_fields = ["university_name"]


class PreviousExamAdmin(admin.ModelAdmin):
    list_display = ["id", "prev_exam_name", "prev_exam_date", "prev_exam_price"]


class ExamAdmin(admin.ModelAdmin):
    list_display = [
        "exam_id", "exam_name", "exam_date", "exam_type",
        "exam_register", "exam_result", "does_answers_added",
        "exam_register_count", "payment_type",
    ]
    list_filter = ["exam_date", "exam_type", "payment_type", "exam_register", "exam_result"]
    search_fields = ["exam_name"]
    filter_horizontal = ["exam_classes", "exam_sections", "exam_groups", "available_previous_exams"]


class CorrectAnswerKeyAdmin(admin.ModelAdmin):
    list_display = ["key_id", "exam", "subject", "variant_name", "subject_order", "is_online"]
    list_filter = ["exam", "subject", "variant_name", "is_online"]
    raw_id_fields = ["exam", "subject", "sinif", "bolme", "qrup"]


class ExamSessionsAdmin(admin.ModelAdmin):
    list_display = ["id", "exam", "time", "session_yer_count"]
    list_filter = ["exam"]
    raw_id_fields = ["exam"]


class RegisterAdmin(admin.ModelAdmin):
    list_display = [
        "id", "first_name", "last_name", "student_reg_number",
        "exam_id", "is_paid", "payment_status", "payment_method",
    ]
    list_filter = ["exam_id", "is_paid", "payment_status", "payment_method"]
    search_fields = ["first_name", "last_name", "student_reg_number", "phone"]


class StudentCabinetAdmin(admin.ModelAdmin):
    list_display = [
        "id", "user", "work_number", "is_course_student",
        "student_verification_status", "is_active",
    ]
    list_filter = ["is_active", "is_course_student", "student_verification_status"]
    search_fields = ["work_number", "phone"]
    raw_id_fields = ["user", "school_new", "district"]


class ExamParticipationAdmin(admin.ModelAdmin):
    list_display = [
        "id", "student", "exam", "is_quiz", "status",
        "attempt_count", "score",
    ]
    list_filter = ["status", "is_quiz", "is_online"]
    raw_id_fields = ["student", "exam", "register"]


class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "participation", "attempt_number", "attempt_type"]
    raw_id_fields = ["participation", "assignment", "sagird_result", "register"]


class OnlineExamAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "id", "student", "exam_name", "exam_id", "variant_name",
        "status", "is_quiz", "attempt_number", "can_view_result",
    ]
    list_filter = ["status", "is_quiz", "exam_type"]
    search_fields = ["exam_name"]
    raw_id_fields = ["student", "sinif", "bolme", "qrup", "register", "participation", "sagird_result"]


class StudentExamSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "assignment", "started_at", "submitted_at", "is_submitted"]
    raw_id_fields = ["assignment", "result"]


class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ["id", "session", "question_number", "subject", "question_type"]
    list_filter = ["subject", "question_type"]
    raw_id_fields = ["session"]


class SagirdResultAdmin(admin.ModelAdmin):
    list_display = [
        "id", "last_name", "first_name", "exam_id",
        "student_reg_number", "total_point", "attempt_number",
    ]
    list_filter = ["exam_id"]
    search_fields = ["first_name", "last_name", "student_reg_number"]
    raw_id_fields = ["session", "register", "cabinet"]


class MarkerAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "role", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["name", "email"]
    filter_horizontal = ["allowed_subjects"]


class QuestionAssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "exam", "subject", "question_number", "required_marker_count"]
    list_filter = ["exam", "subject"]
    raw_id_fields = ["exam", "subject", "head_marker"]
    filter_horizontal = ["assigned_markers"]


class StudentAnswerGradingAdmin(admin.ModelAdmin):
    list_display = [
        "id", "subject_name", "question_number", "status",
        "final_score", "final_fraction", "is_suspicious",
    ]
    list_filter = ["status", "is_suspicious", "subject_name"]
    raw_id_fields = ["result", "assignment"]


class IndividualGradeAdmin(admin.ModelAdmin):
    list_display = [
        "id", "answer_grading", "marker", "fraction",
        "numeric_score", "is_suspicious", "is_head_marker_override",
    ]
    raw_id_fields = ["answer_grading", "marker"]


class AdminUserAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "position", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["first_name", "last_name"]
    raw_id_fields = ["user", "created_by"]


class ModuleAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "display_name", "order"]
    ordering = ["order"]


class ModuleListAdmin(admin.ModelAdmin):
    list_display = ["id", "module", "name", "model_name", "api_endpoint"]
    raw_id_fields = ["module"]


class ListFieldAdmin(admin.ModelAdmin):
    list_display = ["id", "module_list", "name", "field_type"]
    raw_id_fields = ["module_list"]


class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "admin_user", "module",
        "can_view", "can_create", "can_edit", "can_delete",
    ]
    raw_id_fields = ["admin_user", "module"]


class ListPermissionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "admin_user", "module_list",
        "can_view", "can_create", "can_edit", "can_delete",
    ]
    raw_id_fields = ["admin_user", "module_list"]


class FieldPermissionAdmin(admin.ModelAdmin):
    list_display = ["id", "admin_user", "list_field", "can_view", "can_edit"]
    raw_id_fields = ["admin_user", "list_field"]


class PermissionLogAdmin(admin.ModelAdmin):
    list_display = ["id", "admin_user", "action", "module_name", "created_at"]
    list_filter = ["action"]
    raw_id_fields = ["admin_user"]


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "start_datetime", "deadline", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


class CompetitionQuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "competition", "order", "answer_type", "points", "duration_seconds"]
    list_filter = ["competition", "answer_type"]
    raw_id_fields = ["competition"]


class CompetitionParticipantAdmin(admin.ModelAdmin):
    list_display = ["id", "competition", "student", "total_score", "joined_at"]
    raw_id_fields = ["competition", "student"]


class CompetitionQuestionAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "participant", "question", "is_correct", "points_earned", "is_timeout"]
    raw_id_fields = ["participant", "question"]


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "notification_type"]
    list_filter = ["notification_type"]


class CabinetNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "student", "is_read", "created_at"]
    list_filter = ["is_read"]
    raw_id_fields = ["student", "template"]


class CabinetActivityAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "activity_type", "exam_name", "created_at"]
    list_filter = ["activity_type"]
    raw_id_fields = ["student"]


class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "identifier", "identifier_type", "ip_address", "is_successful", "created_at"]
    list_filter = ["is_successful", "identifier_type"]


class LoginBlockAdmin(admin.ModelAdmin):
    list_display = ["id", "identifier", "blocked_until", "attempt_count"]


class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "purpose", "is_used", "expires_at", "created_at"]
    list_filter = ["is_used", "purpose"]


class WhatsAppTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "exam", "name", "template_type"]
    list_filter = ["template_type"]
    raw_id_fields = ["exam"]


class ExamRecordingAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "recording_type", "file_size", "uploaded_at"]
    list_filter = ["recording_type"]
    raw_id_fields = ["assignment", "session", "student"]


class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "payment_type", "is_active"]
    list_filter = ["payment_type", "is_active"]
    raw_id_fields = ["student"]


class CourseTeacherScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "teacher", "monthly_payment"]
    raw_id_fields = ["teacher"]


class CoursePaymentRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "enrollment", "amount", "payment_date", "month_year"]
    raw_id_fields = ["enrollment"]


admin_site.register(ExamType, ExamTypeAdmin)
admin_site.register(Subject, SubjectAdmin)
admin_site.register(Sinif, SinifAdmin)
admin_site.register(Bolme, BolmeAdmin)
admin_site.register(Qrup, QrupAdmin)
admin_site.register(District, DistrictAdmin)
admin_site.register(SchoolType, SchoolTypeAdmin)
admin_site.register(School, SchoolAdmin)
admin_site.register(Universities, UniversitiesAdmin)
admin_site.register(PreviousExam, PreviousExamAdmin)
admin_site.register(Exam, ExamAdmin)
admin_site.register(CorrectAnswerKey, CorrectAnswerKeyAdmin)
admin_site.register(ExamSessions, ExamSessionsAdmin)
admin_site.register(Register, RegisterAdmin)
admin_site.register(StudentCabinet, StudentCabinetAdmin)
admin_site.register(ExamParticipation, ExamParticipationAdmin)
admin_site.register(ExamAttempt, ExamAttemptAdmin)
admin_site.register(OnlineExamAssignment, OnlineExamAssignmentAdmin)
admin_site.register(StudentExamSession, StudentExamSessionAdmin)
admin_site.register(StudentAnswer, StudentAnswerAdmin)
admin_site.register(SagirdResult, SagirdResultAdmin)
admin_site.register(Marker, MarkerAdmin)
admin_site.register(QuestionAssignment, QuestionAssignmentAdmin)
admin_site.register(StudentAnswerGrading, StudentAnswerGradingAdmin)
admin_site.register(IndividualGrade, IndividualGradeAdmin)
admin_site.register(AdminUser, AdminUserAdmin)
admin_site.register(Module, ModuleAdmin)
admin_site.register(ModuleList, ModuleListAdmin)
admin_site.register(ListField, ListFieldAdmin)
admin_site.register(ModulePermission, ModulePermissionAdmin)
admin_site.register(ListPermission, ListPermissionAdmin)
admin_site.register(FieldPermission, FieldPermissionAdmin)
admin_site.register(PermissionLog, PermissionLogAdmin)
admin_site.register(Competition, CompetitionAdmin)
admin_site.register(CompetitionQuestion, CompetitionQuestionAdmin)
admin_site.register(CompetitionParticipant, CompetitionParticipantAdmin)
admin_site.register(CompetitionQuestionAttempt, CompetitionQuestionAttemptAdmin)
admin_site.register(NotificationTemplate, NotificationTemplateAdmin)
admin_site.register(CabinetNotification, CabinetNotificationAdmin)
admin_site.register(CabinetActivity, CabinetActivityAdmin)
admin_site.register(LoginAttempt, LoginAttemptAdmin)
admin_site.register(LoginBlock, LoginBlockAdmin)
admin_site.register(PasswordResetOTP, PasswordResetOTPAdmin)
admin_site.register(WhatsAppTemplate, WhatsAppTemplateAdmin)
admin_site.register(ExamRecording, ExamRecordingAdmin)
admin_site.register(CourseEnrollment, CourseEnrollmentAdmin)
admin_site.register(CourseTeacherSchedule, CourseTeacherScheduleAdmin)
admin_site.register(CoursePaymentRecord, CoursePaymentRecordAdmin)
