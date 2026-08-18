from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView
from django.db.models import Q
from django.http import JsonResponse
import json

from core.views import StaffRequiredMixin
from attendance.models import Attendance
from attendance.forms import AttendanceForm
from courses.models import Group
from students.models import Student

from rest_framework import viewsets, serializers


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = '__all__'

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student__user', 'group', 'marked_by').all()
    serializer_class = AttendanceSerializer
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name')


class AttendanceListView(StaffRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/list.html'
    context_object_name = 'attendances'

    def _is_teacher(self):
        return not self.request.user.is_superuser and hasattr(self.request.user, 'teacher_profile')

    def get_queryset(self):
        qs = Attendance.objects.select_related('student__user', 'group').all()
        if self._is_teacher():
            qs = qs.filter(group__teacher=self.request.user.teacher_profile)
        group_id = self.request.GET.get('group')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if group_id:
            qs = qs.filter(group_id=group_id)
        if date_from:
            qs = qs.filter(lesson_date__gte=date_from)
        if date_to:
            qs = qs.filter(lesson_date__lte=date_to)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self._is_teacher():
            context['groups'] = Group.objects.filter(is_active=True, teacher=self.request.user.teacher_profile)
        else:
            context['groups'] = Group.objects.filter(is_active=True)
        context['selected_group'] = self.request.GET.get('group', '')
        return context


class AttendanceCreateView(StaffRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/form.html'
    success_url = '/attendance/'


class AttendanceMarkView(StaffRequiredMixin, View):
    """Lesson-based attendance marking - JS style like Jet Academy"""

    def _is_teacher(self):
        return not self.request.user.is_superuser and hasattr(self.request.user, 'teacher_profile')

    def get(self, request):
        group_id = request.GET.get('group')
        lesson_date = request.GET.get('date', timezone.now().date())
        if self._is_teacher():
            groups = Group.objects.filter(is_active=True, teacher=request.user.teacher_profile).select_related('course')
        else:
            groups = Group.objects.filter(is_active=True).select_related('course')

        students = []
        selected_group = None
        if group_id:
            selected_group = get_object_or_404(Group, id=group_id)
            group_students = selected_group.group_students.filter(
                status='active'
            ).select_related('student__user')
            for gs in group_students:
                att, _ = Attendance.objects.get_or_create(
                    student=gs.student,
                    group=selected_group,
                    lesson_date=lesson_date,
                    defaults={'status': 'present'}
                )
                students.append({
                    'id': gs.student.id,
                    'full_name': gs.student.user.get_full_name(),
                    'status': att.status,
                    'late_minutes': att.late_minutes,
                    'reason': att.reason,
                    'attendance_id': att.id,
                })

        return render(request, 'attendance/mark.html', {
            'groups': groups,
            'selected_group': selected_group,
            'lesson_date': lesson_date,
            'students': students,
        })

    def post(self, request):
        group_id = request.POST.get('group')
        lesson_date = request.POST.get('date', timezone.now().date())
        selected_group = get_object_or_404(Group, id=group_id)

        attendance_data = {}
        for key, value in request.POST.items():
            if key.startswith('status_'):
                student_id = key.replace('status_', '')
                attendance_data[student_id] = {
                    'status': value,
                    'late_minutes': request.POST.get(f'late_{student_id}', 0),
                    'reason': request.POST.get(f'reason_{student_id}', ''),
                }

        for gs in selected_group.group_students.filter(status='active').select_related('student'):
            sid = str(gs.student.id)
            data = attendance_data.get(sid, {})
            Attendance.objects.update_or_create(
                student=gs.student,
                group=selected_group,
                lesson_date=lesson_date,
                defaults={
                    'status': data.get('status', 'present'),
                    'late_minutes': int(data.get('late_minutes', 0)),
                    'reason': data.get('reason', ''),
                    'marked_by': request.user,
                }
            )

        messages.success(request, 'Davamiyyət qeyd edildi!')
        return redirect(f"{reverse('attendance_mark')}?group={group_id}&date={lesson_date}")


class AttendanceCalendarView(StaffRequiredMixin, View):
    """Monthly calendar-based attendance per group."""

    def _is_teacher(self):
        return not self.request.user.is_superuser and hasattr(self.request.user, 'teacher_profile')

    def get(self, request):
        from datetime import date
        import calendar as cal_mod

        group_id = request.GET.get('group')
        month = int(request.GET.get('month', timezone.now().month))
        year = int(request.GET.get('year', timezone.now().year))

        if self._is_teacher():
            groups = Group.objects.filter(is_active=True, teacher=request.user.teacher_profile).select_related('course', 'teacher__user')
        else:
            groups = Group.objects.filter(is_active=True).select_related('course', 'teacher__user')
        selected_group = None
        lesson_dates = []
        students = []
        attendance_map = {}
        total_marked = 0
        total_cells = 0

        WEEKDAY_MAP = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6,
        }
        WEEKDAY_AZ = {
            0: 'B.e', 1: 'Ç.a', 2: 'Çrş', 3: 'C.a', 4: 'Cüm', 5: 'Şnb', 6: 'Bzr',
        }

        if group_id:
            selected_group = get_object_or_404(Group, id=group_id)

            weekdays = selected_group.weekdays or []
            weekday_nums = [WEEKDAY_MAP[d] for d in weekdays if d in WEEKDAY_MAP]

            num_days = cal_mod.monthrange(year, month)[1]
            for day in range(1, num_days + 1):
                d = date(year, month, day)
                if d.weekday() in weekday_nums:
                    lesson_dates.append(d)

            group_students = selected_group.group_students.filter(
                status='active'
            ).select_related('student__user').order_by('student__user__first_name')

            students = [{
                'id': gs.student.id,
                'name': gs.student.user.get_full_name(),
            } for gs in group_students]

            if lesson_dates:
                records = Attendance.objects.filter(
                    group=selected_group,
                    lesson_date__in=lesson_dates,
                    student__in=[gs.student for gs in group_students]
                ).select_related('student')

                for rec in records:
                    key = f"{rec.student_id}_{rec.lesson_date}"
                    attendance_map[key] = rec.status
                    total_marked += 1
                    total_cells += 1

        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year

        if month == 12:
            next_month, next_year = 1, year + 1
        else:
            next_month, next_year = month + 1, year

        month_names = {
            1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
            5: 'May', 6: 'İyun', 7: 'İyul', 8: 'Avqust',
            9: 'Sentyabr', 10: 'Oktyabr', 11: 'Noyabr', 12: 'Dekabr',
        }

        total_possible = len(students) * len(lesson_dates)
        if total_possible > 0:
            present_count = sum(1 for v in attendance_map.values() if v == 'present')
            att_pct = round(present_count / total_possible * 100, 1)
        else:
            att_pct = 0

        weekday_labels = [WEEKDAY_AZ[WEEKDAY_MAP[d]] for d in (selected_group.weekdays or []) if d in WEEKDAY_MAP]

        context = {
            'title': 'Davamiyyət',
            'groups': groups,
            'selected_group': selected_group,
            'lesson_dates': lesson_dates,
            'students': students,
            'attendance_map_json': json.dumps(attendance_map),
            'month': month,
            'year': year,
            'month_name': month_names.get(month, ''),
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'total_marked': total_marked,
            'total_cells': total_possible,
            'att_pct': att_pct,
            'weekday_labels': ', '.join(weekday_labels),
        }
        return render(request, 'attendance/calendar.html', context)

    def post(self, request):
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            lesson_date = data.get('lesson_date')
            status = data.get('status')
            group_id = data.get('group_id')

            student = Student.objects.get(id=student_id)
            group = Group.objects.get(id=group_id)

            Attendance.objects.update_or_create(
                student=student,
                group=group,
                lesson_date=lesson_date,
                defaults={
                    'status': status,
                    'marked_by': request.user,
                }
            )

            return JsonResponse({'success': True, 'status': status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
