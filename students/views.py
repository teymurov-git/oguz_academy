from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from core.views import StaffRequiredMixin
from students.models import Student
from students.forms import StudentForm

from rest_framework import viewsets
from students.models import Student
from students.serializers import StudentListSerializer, StudentDetailSerializer


class StudentListView(StaffRequiredMixin, ListView):
    model = Student
    template_name = 'student_list.html'
    context_object_name = 'students'


class StudentCreateView(StaffRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'student_form.html'
    success_url = reverse_lazy('student_list')


class StudentUpdateView(StaffRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'student_form.html'
    success_url = reverse_lazy('student_list')


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'parent').all()
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'student_id', 'phone')

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        return StudentDetailSerializer
