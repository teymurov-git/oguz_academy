from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from core.views import StaffRequiredMixin
from attendance.models import Attendance
from attendance.forms import AttendanceForm


class AttendanceListView(StaffRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance_list.html'
    context_object_name = 'attendances'


class AttendanceCreateView(StaffRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance_form.html'
    success_url = reverse_lazy('attendance_list')
