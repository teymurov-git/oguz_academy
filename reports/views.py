from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from students.models import Student
        from teachers.models import Teacher
        from courses.models import Group, Course
        from payments.models import Payment

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total_students = Student.objects.filter(is_active=True).count()
        active_groups = Group.objects.filter(status='active').count()
        active_teachers = Teacher.objects.filter(is_active=True).count()
        total_courses = Course.objects.filter(is_active=True).count()
        new_students = Student.objects.filter(enrollment_date__gte=month_start).count()

        monthly_payments = Payment.objects.filter(
            payment_date__gte=month_start, status='paid'
        ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0

        pending_payments = Payment.objects.filter(status='pending').count()

        return Response({
            'total_students': total_students,
            'active_groups': active_groups,
            'active_teachers': active_teachers,
            'total_courses': total_courses,
            'new_students_this_month': new_students,
            'monthly_income': float(monthly_payments),
            'pending_payments': pending_payments,
        })
