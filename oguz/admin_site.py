from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect, resolve_url
from django.contrib.auth import get_user_model, logout as auth_logout


class OguzAdminSite(AdminSite):
    site_title = _('Oğuz Tədris Mərkəzi')
    site_header = _('Oğuz Tədris Mərkəzi')
    index_title = _('İdarəetmə Paneli')
    login_template = 'admin/login.html'
    index_template = 'admin/index.html'

    # ── Permission codenames → sidebar/menu mapping ──
    SECTION_PERMISSIONS = {
        'dashboard':   [],  # everyone gets dashboard
        'users':       ['view_students', 'add_students', 'edit_students', 'delete_students',
                        'view_teachers', 'add_teachers', 'edit_teachers', 'delete_teachers'],
        'students':    ['view_students'],
        'teachers':    ['view_teachers'],
        'courses':     ['view_courses'],
        'groups':      ['view_groups'],
        'payments':    ['view_payments'],
        'attendance':  ['view_attendance'],
        'exams':       ['view_exams'],
        'schedule':    [],
        'employees':   [],
        'roles':       [],
        'settings':    ['view_settings'],
    }

    def _get_user_roles(self, user):
        """Return (role_names, role_slugs, permissions_set) for a user."""
        if not user.is_authenticated:
            return [], [], set()
        from roles.models import UserRole
        user_roles = (
            UserRole.objects
            .filter(user=user)
            .select_related('role')
        )
        role_names = [ur.role.name for ur in user_roles]
        role_slugs = [ur.role.slug for ur in user_roles]
        perms = set()

        for ur in user_roles:
            for rp in ur.role.role_permissions.select_related('permission').all():
                perms.add(rp.permission.codename)

        return role_names, role_slugs, perms

    def each_context(self, request):
        """Add role/permission context to every admin template.
        Sidebar flags are primarily provided by oguz.context_processors.sidebar_context.
        This method only adds page-level context for admin-specific pages."""
        context = super().each_context(request)
        user = request.user

        if not user.is_authenticated:
            return context

        # Add user display info
        context['current_user'] = user

        # Academic year selector
        from courses.models import AcademicYear
        all_years = AcademicYear.objects.all()
        context['academic_years'] = all_years
        current_year_id = request.session.get('academic_year_id')
        if current_year_id:
            try:
                context['current_academic_year'] = AcademicYear.objects.get(pk=current_year_id)
            except AcademicYear.DoesNotExist:
                context['current_academic_year'] = None
        else:
            context['current_academic_year'] = AcademicYear.objects.filter(is_current=True).first()

        return context

    def logout(self, request, extra_context=None):
        """Log out and redirect to admin login."""
        auth_logout(request)
        return redirect('admin:login')

    def index(self, request, extra_context=None):
        """Route to role-appropriate dashboard."""
        if not request.user.is_authenticated:
            return redirect('admin:login')

        user = request.user

        if user.is_superuser:
            return redirect('admin_dashboard')

        if user.is_staff:
            from roles.models import UserRole
            user_roles = UserRole.objects.filter(user=user).select_related('role')
            role_slugs = [ur.role.slug for ur in user_roles]

            if any(s in ('super-admin', 'owner', 'administrator') for s in role_slugs):
                return redirect('admin_dashboard')

            if hasattr(user, 'teacher_profile'):
                return redirect('teacher_dashboard')
            if hasattr(user, 'student_profile'):
                return redirect('student_dashboard')

            if any(s == 'muellim' for s in role_slugs):
                return redirect('teacher_dashboard')
            if any(s == 'telebe' for s in role_slugs):
                return redirect('student_dashboard')

        if hasattr(user, 'teacher_profile'):
            return redirect('teacher_dashboard')
        if hasattr(user, 'student_profile'):
            return redirect('student_dashboard')

        from roles.models import UserRole
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        role_slugs = [ur.role.slug for ur in user_roles]

        if any(s in ('super-admin', 'owner', 'administrator') for s in role_slugs):
            return redirect('admin_dashboard')
        if 'muellim' in role_slugs:
            return redirect('teacher_dashboard')
        if 'telebe' in role_slugs:
            return redirect('student_dashboard')

        return redirect('admin_dashboard')

    def app_index(self, request, app_label, extra_context=None):
        """Check role access for app index pages."""
        user = request.user
        extra_context = extra_context or {}

        if not user.is_authenticated or user.is_superuser:
            return super().app_index(request, app_label, extra_context=extra_context)

        if hasattr(user, 'teacher_profile') and app_label in ('courses', 'attendance'):
            return super().app_index(request, app_label, extra_context=extra_context)

        if hasattr(user, 'student_profile') and app_label in ('courses', 'attendance'):
            return super().app_index(request, app_label, extra_context=extra_context)

        if user.is_staff:
            return super().app_index(request, app_label, extra_context=extra_context)

        _, _, perms = self._get_user_roles(user)

        APP_PERMS = {
            'students': 'view_students',
            'teachers': 'view_teachers',
            'courses': 'view_courses',
            'payments': 'view_payments',
            'attendance': 'view_attendance',
            'exam_system': 'view_exams',
            'online_exam': 'view_exams',
            'schedule': 'view_exams',
            'system_settings': 'view_settings',
            'employees': 'view_teachers',
            'roles': 'view_settings',
            'account': 'view_students',
        }

        required = APP_PERMS.get(app_label)
        if required and required not in perms:
            from django.http import Http404
            raise Http404

        return super().app_index(request, app_label, extra_context=extra_context)

    def get_app_list(self, request, app_label=None):
        """Filter app list based on user role permissions."""
        user = request.user
        if not user.is_authenticated:
            return super().get_app_list(request, app_label)

        if user.is_superuser:
            return super().get_app_list(request, app_label)

        is_teacher = hasattr(user, 'teacher_profile')
        is_student = hasattr(user, 'student_profile')

        if not is_teacher and not is_student:
            from roles.models import UserRole
            role_slugs = [ur.role.slug for ur in UserRole.objects.filter(user=user).select_related('role')]
            is_teacher = 'muellim' in role_slugs
            is_student = 'telebe' in role_slugs

        app_list = super().get_app_list(request, app_label)

        if user.is_staff and not is_teacher and not is_student:
            return app_list

        if is_teacher:
            for app in app_list:
                if app['app_label'] == 'courses':
                    app['models'] = [
                        m for m in app.get('models', [])
                        if m['object_name'] in ('Group', 'GroupStudent')
                    ]
            return [app for app in app_list if app['app_label'] in ('courses', 'attendance')]

        if is_student:
            for app in app_list:
                if app['app_label'] == 'courses':
                    app['models'] = [
                        m for m in app.get('models', [])
                        if m['object_name'] in ('Group',)
                    ]
            return [app for app in app_list if app['app_label'] in ('courses', 'attendance')]

        _, _, perms = self._get_user_roles(user)

        APP_VIEW_PERMS = {
            'students': 'view_students',
            'teachers': 'view_teachers',
            'courses': 'view_courses',
            'payments': 'view_payments',
            'attendance': 'view_attendance',
            'exam_system': 'view_exams',
            'online_exam': 'view_exams',
            'schedule': 'view_exams',
            'system_settings': 'view_settings',
            'employees': 'view_teachers',
            'roles': 'view_settings',
            'account': 'view_students',
        }

        filtered = []
        for app in app_list:
            label = app['app_label']
            required = APP_VIEW_PERMS.get(label)
            if required is None or required in perms:
                filtered.append(app)

        return filtered


admin_site = OguzAdminSite(name='admin')

# Force all ModelAdmin classes to use our custom templates
admin.ModelAdmin.change_list_template = 'admin/change_list.html'
admin.ModelAdmin.change_form_template = 'admin/change_form.html'
