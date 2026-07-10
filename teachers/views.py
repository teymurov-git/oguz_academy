from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from core.views import StaffRequiredMixin
from teachers.models import Teacher
from teachers.forms import TeacherForm


class TeacherListView(StaffRequiredMixin, ListView):
    model = Teacher
    template_name = 'teacher_list.html'
    context_object_name = 'teachers'


class TeacherCreateView(StaffRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teacher_form.html'
    success_url = reverse_lazy('teacher_list')


class TeacherUpdateView(StaffRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teacher_form.html'
    success_url = reverse_lazy('teacher_list')
