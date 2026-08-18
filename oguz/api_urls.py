from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from core.views import ContactAPIView
from students.views import StudentViewSet
from teachers.views import TeacherViewSet
from courses.views import CourseCategoryViewSet, CourseViewSet, GroupViewSet, ExamViewSet, ExamRegistrationViewSet
from payments.views import PaymentViewSet, PaymentPlanViewSet
from attendance.views import AttendanceViewSet
from employees.views import EmployeeViewSet, PositionViewSet
from schedule.views import ScheduleViewSet, LessonViewSet, LessonAttendanceViewSet
from system_settings.views import SystemSettingViewSet
from reports.views import DashboardStatsView
from roles.views import RoleViewSet, PermissionViewSet, UserRoleViewSet
from exam_system.views import (
    ExamViewSet as SystemExamViewSet,
    QuestionViewSet,
    VariantViewSet,
    StudentExamViewSet,
    StudentAnswerViewSet,
    MarkerConsensusViewSet,
    CompetitionViewSet,
)

router = DefaultRouter()

router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'course-categories', CourseCategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'exam-registrations', ExamRegistrationViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'payment-plans', PaymentPlanViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'positions', PositionViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'lesson-attendance', LessonAttendanceViewSet)
router.register(r'system-settings', SystemSettingViewSet)
router.register(r'system-exams', SystemExamViewSet, basename='system-exam')
router.register(r'questions', QuestionViewSet)
router.register(r'variants', VariantViewSet)
router.register(r'student-exams', StudentExamViewSet)
router.register(r'student-answers', StudentAnswerViewSet)
router.register(r'marker-consensus', MarkerConsensusViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'user-roles', UserRoleViewSet)

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('contact/', ContactAPIView.as_view(), name='contact_api'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('', include(router.urls)),
    path('online-exam/', include('online_exam.urls')),
]
