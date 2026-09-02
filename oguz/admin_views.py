import json
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from students.models import Student
from teachers.models import Teacher
from courses.models import Course, Group, CourseCategory, AcademicYear
from payments.models import Payment, MonthlyPayment
from attendance.models import Attendance
from employees.models import Employee
from roles.models import Role, UserRole
from account.models import User
from core.models import Contact


def get_user_role(user):
    """Determine user role from UserRole model first, then fallback to profile."""
    if user.is_superuser:
        return 'admin'
    if user.is_staff:
        return 'staff'

    # Check UserRole model
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    role_slugs = [ur.role.slug for ur in user_roles]

    if any(s in ('super-admin', 'owner', 'administrator') for s in role_slugs):
        return 'admin'
    if 'muellim' in role_slugs:
        return 'teacher'
    if 'telebe' in role_slugs:
        return 'student'

    # Fallback: check profile
    if hasattr(user, 'employee_profile'):
        pos = user.employee_profile.position_fk
        if pos and 'müdür' in pos.name.lower():
            return 'branch_manager'
        return 'employee'
    if hasattr(user, 'teacher_profile'):
        return 'teacher'
    if hasattr(user, 'student_profile'):
        return 'student'

    return 'user'


def get_user_permissions(user):
    """Get all permission codenames for a user based on their roles."""
    if user.is_superuser:
        return set()  # empty = all allowed

    if user.is_staff and not hasattr(user, 'teacher_profile') and not hasattr(user, 'student_profile'):
        return set()  # staff without teacher/student profile = full access

    perms = set()
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    for ur in user_roles:
        for rp in ur.role.role_permissions.select_related('permission').all():
            perms.add(rp.permission.codename)

    if not perms:
        if hasattr(user, 'teacher_profile'):
            perms = {
                'view_students', 'view_teachers', 'view_courses', 'view_groups',
                'edit_groups', 'view_payments', 'view_attendance', 'add_attendance',
                'edit_attendance', 'view_exams', 'add_exams', 'grade_exams', 'view_notifications',
            }
        elif hasattr(user, 'student_profile'):
            perms = {
                'view_courses', 'view_groups', 'view_attendance', 'view_payments',
                'view_exams', 'view_notifications',
            }

    return perms


@staff_member_required
def admin_dashboard(request):
    """Full dashboard for admin/owner/superadmin roles."""
    user = request.user
    is_super = user.is_superuser
    user_role = get_user_role(user)
    perms = get_user_permissions(user)

    # Determine data scope
    is_full_access = is_super or user_role in ('admin', 'branch_manager', 'employee', 'staff')

    students = Student.objects.filter(is_active=True)
    teachers = Teacher.objects.filter(is_active=True)
    groups = Group.objects.filter(status='active')
    courses = Course.objects.filter(is_active=True)
    payments = Payment.objects.all()
    attendances = Attendance.objects.all()

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    expected_income = float(students.aggregate(Sum('monthly_payment'))['monthly_payment__sum'] or 0)
    paid_income = float(payments.filter(payment_date__gte=month_start, status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0)
    total_earnings_all = expected_income + paid_income

    total_students = students.count()
    total_att = attendances.filter(lesson_date=now.date()).count()
    present_att = attendances.filter(lesson_date=now.date(), status='present').count()
    attendance_rate = round((present_att / total_att * 100) if total_att > 0 else 0, 1)

    stats = {
        'total_students': total_students,
        'active_students': students.filter(status='active').count(),
        'new_students_this_month': students.filter(enrollment_date__gte=month_start).count(),
        'new_students_last_month': students.filter(enrollment_date__gte=last_month_start, enrollment_date__lt=month_start).count(),
        'total_teachers': teachers.count(),
        'active_teachers': teachers.count(),
        'total_groups': groups.count(),
        'active_groups': groups.count(),
        'expected_income': expected_income,
        'paid_income': paid_income,
        'total_earnings_all': total_earnings_all,
        'attendance_today': total_att,
        'attendance_rate': attendance_rate,
        'attendance_rate_late': round(100 - attendance_rate - 3, 1) if attendance_rate > 0 else 5,
        'attendance_rate_absent': round(100 - attendance_rate - (100 - attendance_rate - 3), 1) if attendance_rate > 0 else 3,
    }

    recent_students = students.select_related('user').order_by('-enrollment_date')[:5]
    recent_payments = payments.select_related('student__user').order_by('-payment_date')[:5]
    upcoming_groups = groups.select_related('course', 'teacher__user').order_by('start_date')[:5]
    recent_messages = Contact.objects.order_by('-created_at')[:5]

    months = []
    income_data = []
    for i in range(5, -1, -1):
        ms = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        me = (ms + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        months.append(ms.strftime('%b'))
        income_data.append(float(payments.filter(payment_date__gte=ms, payment_date__lte=me, status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0))

    chart_data = {'months': months, 'income': income_data}

    context = {
        'title': 'Panel',
        'stats': stats,
        'recent_students': recent_students,
        'recent_payments': recent_payments,
        'upcoming_groups': upcoming_groups,
        'recent_messages': recent_messages,
        'chart_data': chart_data,
        'is_super': is_super,
        'user_role': user_role,
    }
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def teacher_dashboard(request):
    """Dashboard for teachers — only their groups and students."""
    user = request.user
    teacher = getattr(user, 'teacher_profile', None)

    if not teacher:
        # Try to find teacher by UserRole
        ur = UserRole.objects.filter(user=user, role__slug='muellim').select_related('role').first()
        if not ur:
            return render(request, 'admin/no_access.html', {
                'message': 'Müəllim profili tapılmadı',
                'title': 'Giriş İnzibati',
            })
        # Try getting teacher from queryset
        teacher = Teacher.objects.filter(user=user).first()
        if not teacher:
            return render(request, 'admin/no_access.html', {
                'message': 'Müəllim profili tapılmadı',
                'title': 'Giriş İnzibati',
            })

    groups = Group.objects.filter(teacher=teacher, status='active')
    students = Student.objects.filter(groupstudent__group__in=groups, is_active=True).distinct()

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    attendances = Attendance.objects.filter(student__in=students, lesson_date__gte=month_start)
    total_att = attendances.count()
    present_att = attendances.filter(status='present').count()
    attendance_rate = round((present_att / total_att * 100) if total_att > 0 else 0, 1)

    monthly_income = float(Payment.objects.filter(
        student__in=students, payment_date__gte=month_start, status='paid'
    ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0)

    stats = {
        'my_groups': groups.count(),
        'my_students': students.count(),
        'lessons_this_month': attendances.values('lesson_date').distinct().count(),
        'attendance_rate': attendance_rate,
        'monthly_income': monthly_income,
    }

    recent_attendance = attendances.select_related('student__user', 'group').order_by('-lesson_date')[:10]
    my_groups_list = groups.select_related('course').order_by('schedule_text')[:5]
    recent_payments = Payment.objects.filter(
        student__in=students
    ).select_related('student__user').order_by('-payment_date')[:5]

    # Chart data
    months = []
    income_data = []
    att_data = []
    for i in range(5, -1, -1):
        ms = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        me = (ms + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        months.append(ms.strftime('%b'))
        income_data.append(float(Payment.objects.filter(
            student__in=students, payment_date__gte=ms, payment_date__lte=me, status='paid'
        ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0))
        month_att = Attendance.objects.filter(student__in=students, lesson_date__gte=ms.date(), lesson_date__lte=me.date())
        month_total = month_att.count()
        month_present = month_att.filter(status='present').count()
        att_data.append(round((month_present / month_total * 100) if month_total > 0 else 0, 1))

    chart_data = {'months': months, 'income': income_data, 'attendance': att_data}

    context = {
        'title': 'Müəllim Paneli',
        'teacher': teacher,
        'stats': stats,
        'recent_attendance': recent_attendance,
        'recent_payments': recent_payments,
        'my_groups': my_groups_list,
        'chart_data': chart_data,
        'user_role': 'teacher',
    }
    return render(request, 'admin/teacher_dashboard.html', context)


@staff_member_required
def student_dashboard(request):
    """Dashboard for students — only their info."""
    user = request.user
    student = getattr(user, 'student_profile', None)

    if not student:
        # Try UserRole
        ur = UserRole.objects.filter(user=user, role__slug='telebe').select_related('role').first()
        if not ur:
            return render(request, 'admin/no_access.html', {
                'message': 'Tələbə profili tapılmadı',
                'title': 'Giriş İnzibati',
            })
        student = Student.objects.filter(user=user).first()
        if not student:
            return render(request, 'admin/no_access.html', {
                'message': 'Tələbə profili tapılmadı',
                'title': 'Giriş İnzibati',
            })

    groups = Group.objects.filter(group_students__student=student, status='active')
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    attendances = Attendance.objects.filter(student=student, lesson_date__gte=month_start)
    payments = Payment.objects.filter(student=student)

    total_att = attendances.count()
    present_att = attendances.filter(status='present').count()
    attendance_rate = round((present_att / total_att * 100) if total_att > 0 else 0, 1)

    total_paid = float(payments.filter(status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0)
    pending_amount = float(payments.filter(status='pending').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0)

    stats = {
        'my_groups': groups.count(),
        'my_total_groups': groups.count(),
        'attendance_rate': attendance_rate,
        'present_count': present_att,
        'absent_count': total_att - present_att,
        'total_lessons': total_att,
        'pending_payments': payments.filter(status='pending').count(),
        'paid_payments': payments.filter(status='paid').count(),
        'total_paid': total_paid,
        'pending_amount': pending_amount,
    }

    recent_attendance = attendances.select_related('group__course').order_by('-lesson_date')[:10]
    recent_payments = payments.order_by('-payment_date')[:5]
    my_groups_list = groups.select_related('course', 'teacher__user').order_by('schedule_text')

    # Chart data — attendance by month
    months = []
    att_rates = []
    for i in range(5, -1, -1):
        ms = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        me = (ms + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        months.append(ms.strftime('%b'))
        month_att = Attendance.objects.filter(student=student, lesson_date__gte=ms.date(), lesson_date__lte=me.date())
        m_total = month_att.count()
        m_present = month_att.filter(status='present').count()
        att_rates.append(round((m_present / m_total * 100) if m_total > 0 else 0, 1))

    chart_data = {'months': months, 'attendance': att_rates}

    context = {
        'title': 'Tələbə Paneli',
        'student': student,
        'stats': stats,
        'recent_attendance': recent_attendance,
        'recent_payments': recent_payments,
        'my_groups': my_groups_list,
        'chart_data': chart_data,
        'user_role': 'student',
    }
    return render(request, 'admin/student_dashboard.html', context)


@staff_member_required
def switch_academic_year(request):
    """Switch the active academic year via session."""
    year_id = request.GET.get('year_id')
    if year_id:
        request.session['academic_year_id'] = year_id
    else:
        request.session.pop('academic_year_id', None)
    return redirect(request.META.get('HTTP_REFERER', '/admin/dashboard/'))


MONTHS_AZ = {1: 'Yan', 2: 'Fev', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'İyn', 7: 'İyl', 8: 'Avq', 9: 'Sen', 10: 'Okt', 11: 'Noy', 12: 'Dek'}
MONTHS_ORDER = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]  # Sep → Aug
MONTHS_ORDER_NAMES = [(m, MONTHS_AZ[m]) for m in MONTHS_ORDER]
STATUS_ICON = {'paid': '✓', 'overdue': '!', 'not_paid': '—'}
STATUS_LABEL = {'paid': 'Ödənilib', 'overdue': 'Gecikib', 'not_paid': 'Ödənməyib'}
STATUS_CYCLE = ['not_paid', 'paid', 'overdue']  # click cycles: not_paid → paid → overdue → not_paid


@staff_member_required
def payments_annual(request):
    year_id = request.session.get('academic_year_id')
    if not year_id:
        year = AcademicYear.objects.filter(is_current=True).first()
    else:
        year = get_object_or_404(AcademicYear, pk=year_id)

    students_qs = Student.objects.filter(is_active=True)
    if year:
        students_qs = students_qs.filter(academic_year=year)

    group_id = request.GET.get('group')
    selected_group = None
    if group_id:
        selected_group = get_object_or_404(Group, pk=group_id)
        students_qs = students_qs.filter(groupstudent__group=selected_group)

    students_qs = students_qs.select_related('user').distinct()

    # Determine the display year: use the academic year's start_year
    display_year = year.start_date.year if year else timezone.now().year

    # Prefetch existing monthly payments for all students in bulk
    existing = {}
    mps = MonthlyPayment.objects.filter(
        student__in=students_qs,
        year__in=[display_year, display_year + 1],
    )
    for mp in mps:
        key = (mp.student_id, mp.month, mp.year)
        existing[key] = mp

    # Build table data
    table_rows = []
    total_paid = 0
    for student in students_qs:
        row = {'student': student, 'cells': []}
        for m in MONTHS_ORDER:
            yr = display_year if m >= 9 else display_year + 1
            key = (student.id, m, yr)
            mp = existing.get(key)
            if mp:
                status = mp.status
                amount = float(mp.amount)
            else:
                status = 'not_paid'
                amount = float(student.monthly_payment or 0)
            if status == 'paid':
                total_paid += amount
            row['cells'].append({
                'month': m,
                'year': yr,
                'status': status,
                'amount': amount,
                'status_display': STATUS_LABEL[status],
                'icon': STATUS_ICON[status],
            })
        table_rows.append(row)

    total_students = students_qs.count()
    expected_total = sum(float(s.monthly_payment or 0) for s in students_qs) * 12

    # Filter context
    groups = Group.objects.all()
    if year:
        groups = groups.filter(academic_year=year)

    # Year navigation
    all_years = AcademicYear.objects.all().order_by('start_date')
    year_list = list(all_years)
    prev_year = next_year = None
    if year and year_list:
        idx = next((i for i, y in enumerate(year_list) if y.pk == year.pk), -1)
        if idx > 0:
            prev_year = year_list[idx - 1]
        if idx < len(year_list) - 1:
            next_year = year_list[idx + 1]

    context = {
        'title': 'İllik Ödənişlər',
        'table_rows': table_rows,
        'total_students': total_students,
        'expected_total': expected_total,
        'total_paid': total_paid,
        'display_year': display_year,
        'months_order_names': MONTHS_ORDER_NAMES,
        'status_icon': STATUS_ICON,
        'status_label': STATUS_LABEL,
        'current_year': year,
        'prev_year': prev_year,
        'next_year': next_year,
        'groups': groups,
        'selected_group': selected_group,
    }
    return render(request, 'admin/payments_annual.html', context)


@require_POST
@staff_member_required
def toggle_monthly_payment(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        month = data.get('month')
        year = data.get('year')
    except (json.JSONDecodeError, TypeError):
        return HttpResponseBadRequest('Invalid JSON')

    if not all([student_id, month, year]):
        return HttpResponseBadRequest('Missing parameters')

    student = get_object_or_404(Student, pk=student_id)
    amount = float(student.monthly_payment or 0)

    mp, _ = MonthlyPayment.objects.get_or_create(
        student=student,
        month=month,
        year=year,
        defaults={'amount': amount, 'status': 'not_paid'},
    )

    # Cycle status (also for newly created records: not_paid → paid → overdue → not_paid)
    cur = mp.status
    idx = STATUS_CYCLE.index(cur) if cur in STATUS_CYCLE else 0
    next_idx = (idx + 1) % len(STATUS_CYCLE)
    mp.status = STATUS_CYCLE[next_idx]
    mp.amount = amount
    if mp.status == 'paid':
        mp.paid_at = timezone.now()
    else:
        mp.paid_at = None
    mp.save()

    return JsonResponse({
        'status': mp.status,
        'icon': STATUS_ICON[mp.status],
        'label': STATUS_LABEL[mp.status],
        'amount': float(mp.amount),
    })
