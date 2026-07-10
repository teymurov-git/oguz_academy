from django.urls import path
from courses.views import (
    AbiturientView, DjangoView, InformaticsView, LanguageView,
    LyceumView, MiddleSchoolView, MiqView, PythonView,
    ExamListView, ExamDetailView,
    CourseListView, CourseCreateView, CourseUpdateView,
    GroupListView, GroupCreateView, GroupUpdateView,
)

urlpatterns = [
    path('abiturient/', AbiturientView.as_view(), name='abiturient'),
    path('django/', DjangoView.as_view(), name='django'),
    path('informatics/', InformaticsView.as_view(), name='informatics'),
    path('language/', LanguageView.as_view(), name='language'),
    path('lyceum/', LyceumView.as_view(), name='lyceum'),
    path('middleschool/', MiddleSchoolView.as_view(), name='middleschool'),
    path('miq/', MiqView.as_view(), name='miq'),
    path('python/', PythonView.as_view(), name='python'),
    path('exams/', ExamListView.as_view(), name='exam_list'),
    path('exams/<slug:slug>/', ExamDetailView.as_view(), name='exam_detail'),
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/add/', CourseCreateView.as_view(), name='course_add'),
    path('courses/<int:pk>/edit/', CourseUpdateView.as_view(), name='course_edit'),
    path('groups/', GroupListView.as_view(), name='group_list'),
    path('groups/add/', GroupCreateView.as_view(), name='group_add'),
    path('groups/<int:pk>/edit/', GroupUpdateView.as_view(), name='group_edit'),
]