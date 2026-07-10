from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, ListView, UpdateView

from core.views import StaffRequiredMixin
from courses.models import Exam, Course, Group
from courses.forms import ExamRegistrationForm, CourseForm, GroupForm


class AbiturientView(TemplateView):
    template_name = 'abiturient.html'


class DjangoView(TemplateView):
    template_name = 'django.html'


class InformaticsView(TemplateView):
    template_name = 'informatics.html'


class LanguageView(TemplateView):
    template_name = 'language.html'


class LyceumView(TemplateView):
    template_name = 'lyceum.html'


class MiddleSchoolView(TemplateView):
    template_name = 'middle-school.html'


class MiqView(TemplateView):
    template_name = 'miq.html'


class PythonView(TemplateView):
    template_name = 'python.html'


class ExamListView(TemplateView):
    template_name = 'exam_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = Exam.objects.filter(is_active=True).order_by('-date')
        return context


class ExamDetailView(CreateView):
    template_name = 'exam_detail.html'
    form_class = ExamRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = get_object_or_404(Exam, slug=self.kwargs['slug'], is_active=True)
        return context

    def form_valid(self, form):
        exam = get_object_or_404(Exam, slug=self.kwargs['slug'], is_active=True)
        form.instance.exam = exam
        messages.success(self.request, 'Qeydiyyatınız qəbul edildi!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('exam_detail', kwargs={'slug': self.kwargs['slug']})


class CourseListView(StaffRequiredMixin, ListView):
    model = Course
    template_name = 'course_list.html'
    context_object_name = 'courses'


class CourseCreateView(StaffRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course_form.html'
    success_url = reverse_lazy('course_list')


class CourseUpdateView(StaffRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'course_form.html'
    success_url = reverse_lazy('course_list')


class GroupListView(StaffRequiredMixin, ListView):
    model = Group
    template_name = 'group_list.html'
    context_object_name = 'groups'


class GroupCreateView(StaffRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'group_form.html'
    success_url = reverse_lazy('group_list')


class GroupUpdateView(StaffRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'group_form.html'
    success_url = reverse_lazy('group_list')
