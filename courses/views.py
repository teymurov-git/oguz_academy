from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, ListView, UpdateView
from django.utils import timezone
from django.http import Http404

from core.views import StaffRequiredMixin
from courses.models import Exam, Course, Group
from courses.forms import ExamRegistrationForm, CourseForm, GroupForm

from rest_framework import viewsets
from courses.models import CourseCategory, Course, Group, Exam, ExamRegistration
from courses.serializers import (
    CourseCategorySerializer, CourseSerializer,
    GroupListSerializer, GroupDetailSerializer,
    ExamSerializer, ExamRegistrationSerializer,
)


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
        context['exams'] = Exam.objects.filter(
            is_active=True,
            registration_deadline__gt=timezone.now()
        ).order_by('-date')
        return context


class ExamDetailView(CreateView):
    template_name = 'exam_detail.html'
    form_class = ExamRegistrationForm

    def get_object(self):
        exam = get_object_or_404(Exam, slug=self.kwargs['slug'], is_active=True)
        if exam.registration_deadline <= timezone.now():
            raise Http404("Qeydiyyat müddəti bitmişdir.")
        return exam

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.get_object()
        context['now'] = timezone.now()
        return context

    def form_valid(self, form):
        exam = self.get_object()
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


class CourseCategoryViewSet(viewsets.ModelViewSet):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('category').all()
    serializer_class = CourseSerializer
    search_fields = ('name',)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.select_related('course', 'teacher').prefetch_related('group_students__student__user').all()
    search_fields = ('name',)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and hasattr(user, 'teacher_profile'):
            qs = qs.filter(teacher=user.teacher_profile)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return GroupListSerializer
        return GroupDetailSerializer


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


class ExamRegistrationViewSet(viewsets.ModelViewSet):
    queryset = ExamRegistration.objects.all()
    serializer_class = ExamRegistrationSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = []
        else:
            permission_classes = self.permission_classes
        from rest_framework.permissions import AllowAny
        return [AllowAny()] if self.action == 'create' else [p() for p in permission_classes]
