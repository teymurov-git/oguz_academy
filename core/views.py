from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, CreateView

from core.forms import ContactForm
from students.models import Student
from teachers.models import Teacher
from courses.models import Course, Group
from payments.models import Payment
from attendance.models import Attendance


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class HomeView(TemplateView):
    template_name = 'index.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class EventsView(TemplateView):
    template_name = 'events.html'


class SearchView(TemplateView):
    template_name = 'search.html'


class ContactView(CreateView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        messages.success(self.request, 'Message sent successfully!')
        return super().form_valid(form)


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_count'] = Student.objects.count()
        context['teacher_count'] = Teacher.objects.count()
        context['course_count'] = Course.objects.count()
        context['group_count'] = Group.objects.count()
        context['payment_count'] = Payment.objects.count()
        context['recent_payments'] = Payment.objects.select_related('student__user').order_by('-payment_date')[:10]
        context['today_attendance'] = Attendance.objects.filter(date=timezone.now().date()).count()
        return context