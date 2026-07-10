from django.urls import path
from teachers.views import TeacherListView, TeacherCreateView, TeacherUpdateView

urlpatterns = [
    path('', TeacherListView.as_view(), name='teacher_list'),
    path('add/', TeacherCreateView.as_view(), name='teacher_add'),
    path('<int:pk>/edit/', TeacherUpdateView.as_view(), name='teacher_edit'),
]
