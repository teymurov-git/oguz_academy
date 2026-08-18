from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Parameters
    ExamTypeViewSet, SubjectViewSet, SinifViewSet,
    BolmeViewSet, QrupViewSet, DistrictViewSet,
    SchoolTypeViewSet, SchoolViewSet, UniversitiesViewSet,
    PreviousExamViewSet,
    # Exam core
    ExamViewSet, CorrectAnswerKeyViewSet, ExamSessionsViewSet,
    # Cabinet
    StudentCabinetViewSet, ExamParticipationViewSet,
    OnlineExamAssignmentViewSet, StudentExamSessionViewSet,
    StudentAnswerViewSet,
    # Results
    SagirdResultViewSet,
    # Markers
    MarkerViewSet, QuestionAssignmentViewSet,
    StudentAnswerGradingViewSet, IndividualGradeViewSet,
    MarkerAnswerGradeViewSet,
    # RBAC
    AdminUserViewSet, ModuleViewSet, ModuleListViewSet,
    ListFieldViewSet, ModulePermissionViewSet,
    ListPermissionViewSet, FieldPermissionViewSet,
    PermissionLogViewSet,
    # Competition
    CompetitionViewSet, CompetitionQuestionViewSet,
    CompetitionParticipantViewSet, CompetitionQuestionAttemptViewSet,
    # Notifications
    NotificationTemplateViewSet, CabinetNotificationViewSet,
    CabinetActivityViewSet, LoginAttemptViewSet, LoginBlockViewSet,
    PasswordResetOTPViewSet, WhatsAppTemplateViewSet,
    ExamRecordingViewSet,
    # Course enrollment
    CourseEnrollmentViewSet, CourseTeacherScheduleViewSet,
    CoursePaymentRecordViewSet,
)

router = DefaultRouter()

# Parameters
router.register(r"exam-types", ExamTypeViewSet)
router.register(r"subjects", SubjectViewSet)
router.register(r"classes", SinifViewSet)
router.register(r"sections", BolmeViewSet)
router.register(r"groups", QrupViewSet)
router.register(r"districts", DistrictViewSet)
router.register(r"school-types", SchoolTypeViewSet)
router.register(r"schools", SchoolViewSet)
router.register(r"universities", UniversitiesViewSet)
router.register(r"previous-exams", PreviousExamViewSet)

# Exam core
router.register(r"exams", ExamViewSet)
router.register(r"answer-keys", CorrectAnswerKeyViewSet)
router.register(r"exam-sessions", ExamSessionsViewSet)

# Cabinet
router.register(r"student-cabinets", StudentCabinetViewSet)
router.register(r"participations", ExamParticipationViewSet)
router.register(r"assignments", OnlineExamAssignmentViewSet)
router.register(r"sessions", StudentExamSessionViewSet)
router.register(r"student-answers", StudentAnswerViewSet)

# Results
router.register(r"results", SagirdResultViewSet)

# Markers
router.register(r"markers", MarkerViewSet)
router.register(r"question-assignments", QuestionAssignmentViewSet)
router.register(r"answer-gradings", StudentAnswerGradingViewSet)
router.register(r"individual-grades", IndividualGradeViewSet)
router.register(r"marker-answer-grades", MarkerAnswerGradeViewSet)

# RBAC
router.register(r"admin-users", AdminUserViewSet)
router.register(r"modules", ModuleViewSet)
router.register(r"module-lists", ModuleListViewSet)
router.register(r"list-fields", ListFieldViewSet)
router.register(r"module-permissions", ModulePermissionViewSet)
router.register(r"list-permissions", ListPermissionViewSet)
router.register(r"field-permissions", FieldPermissionViewSet)
router.register(r"permission-logs", PermissionLogViewSet)

# Competition
router.register(r"competitions", CompetitionViewSet)
router.register(r"competition-questions", CompetitionQuestionViewSet)
router.register(r"competition-participants", CompetitionParticipantViewSet)
router.register(r"competition-attempts", CompetitionQuestionAttemptViewSet)

# Notifications
router.register(r"notification-templates", NotificationTemplateViewSet)
router.register(r"cabinet-notifications", CabinetNotificationViewSet)
router.register(r"cabinet-activities", CabinetActivityViewSet)
router.register(r"login-attempts", LoginAttemptViewSet)
router.register(r"login-blocks", LoginBlockViewSet)
router.register(r"password-reset-otps", PasswordResetOTPViewSet)
router.register(r"whatsapp-templates", WhatsAppTemplateViewSet)
router.register(r"exam-recordings", ExamRecordingViewSet)

# Course enrollment
router.register(r"course-enrollments", CourseEnrollmentViewSet)
router.register(r"course-teacher-schedules", CourseTeacherScheduleViewSet)
router.register(r"course-payment-records", CoursePaymentRecordViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
