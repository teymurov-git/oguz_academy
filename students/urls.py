from django.urls import path
from students.views import StudentListView, StudentCreateView, StudentUpdateView

urlpatterns = [
    path('', StudentListView.as_view(), name='student_list'),
    path('add/', StudentCreateView.as_view(), name='student_add'),
    path('<int:pk>/edit/', StudentUpdateView.as_view(), name='student_edit'),
]
