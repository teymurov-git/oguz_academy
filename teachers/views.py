from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from core.views import StaffRequiredMixin
from teachers.models import Teacher
from teachers.forms import TeacherForm

from rest_framework import viewsets
from teachers.serializers import TeacherListSerializer, TeacherDetailSerializer


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


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user', 'employee').all()
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'teacher_id')

    def get_serializer_class(self):
        if self.action == 'list':
            return TeacherListSerializer
        return TeacherDetailSerializer
