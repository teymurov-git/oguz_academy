from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from oguz.admin_views import admin_dashboard, teacher_dashboard, student_dashboard, switch_academic_year, payments_annual, toggle_monthly_payment
from oguz.grading_views import grading_exam_list, grading_enter, grading_results, grading_answer_card
from oguz.exam_manage_views import exam_manage, exam_question_add, exam_question_edit, exam_question_delete, exam_question_reorder
from oguz.exams_views import dim_exam_list, dim_exam_answers, dim_exam_delete, dim_exam_registrations
from exam_system.public_views import public_results
from oguz.admin_site import admin_site


def admin_logout_view(request):
    auth_logout(request)
    return redirect('admin:login')


urlpatterns = [
    path('admin/logout/', admin_logout_view, name='admin_logout'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/teacher-dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('admin/student-dashboard/', student_dashboard, name='student_dashboard'),
    path('admin/switch-year/', switch_academic_year, name='switch_academic_year'),
    path('admin/payments/', payments_annual, name='payments_annual'),
    path('admin/payments/toggle/', toggle_monthly_payment, name='toggle_monthly_payment'),
    path('admin/grading/', grading_exam_list, name='grading_exam_list'),
    path('admin/grading/<uuid:exam_id>/<uuid:student_exam_id>/', grading_enter, name='grading_enter'),
    path('admin/grading/<uuid:exam_id>/results/', grading_results, name='grading_results'),
    path('admin/grading/card/<uuid:student_exam_id>/', grading_answer_card, name='grading_answer_card'),
    path('admin/exam-manage/<uuid:exam_id>/', exam_manage, name='exam_manage'),
    path('admin/exam-manage/<uuid:exam_id>/add/', exam_question_add, name='exam_question_add'),
    path('admin/exam-manage/<uuid:exam_id>/edit/<uuid:question_id>/', exam_question_edit, name='exam_question_edit'),
    path('admin/exam-manage/<uuid:exam_id>/delete/<uuid:question_id>/', exam_question_delete, name='exam_question_delete'),
    path('admin/exam-manage/<uuid:exam_id>/reorder/', exam_question_reorder, name='exam_question_reorder'),
    path('admin/exams/', dim_exam_list, name='dim_exam_list'),
    path('admin/exams/<uuid:exam_id>/answers/', dim_exam_answers, name='dim_exam_answers'),
    path('admin/exams/<uuid:exam_id>/registrations/', dim_exam_registrations, name='dim_exam_registrations'),
    path('admin/exams/<uuid:exam_id>/delete/', dim_exam_delete, name='dim_exam_delete'),
    path('admin/', admin_site.urls),
    path('api/v1/', include('oguz.api_urls')),
    path('', include('account.urls')),
    path('', include('core.urls')),
    path('', include('courses.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('payments/', include('payments.urls')),
    path('attendance/', include('attendance.urls')),
    path('neticelerim/', public_results, name='public_results'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
