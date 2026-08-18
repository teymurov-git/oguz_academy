from roles.models import UserRole


def sidebar_context(request):
    """Provide sidebar visibility flags to ALL templates (admin + dashboard views)."""
    ctx = {}
    user = request.user

    if not user.is_authenticated:
        return ctx

    is_super = user.is_superuser
    is_staff = user.is_staff

    # ── Determine role ──
    role_names = []
    role_slugs = []
    perms = set()
    is_admin_role = False
    is_teacher_role = False
    is_student_role = False

    if is_super:
        is_admin_role = True
        role_names = ['Super Admin']
    elif is_staff:
        user_roles = (
            UserRole.objects
            .filter(user=user)
            .select_related('role')
        )
        role_names = [ur.role.name for ur in user_roles]
        role_slugs = [ur.role.slug for ur in user_roles]

        for ur in user_roles:
            for rp in ur.role.role_permissions.select_related('permission').all():
                perms.add(rp.permission.codename)

        is_admin_role = any(s in ('super-admin', 'owner', 'administrator') for s in role_slugs)
        is_teacher_role = any(s == 'muellim' for s in role_slugs) or hasattr(user, 'teacher_profile')
        is_student_role = any(s == 'telebe' for s in role_slugs) or hasattr(user, 'student_profile')

        if not role_names:
            if is_teacher_role:
                role_names = ['Müəllim']
            elif is_student_role:
                role_names = ['Tələbə']
            elif is_staff:
                is_admin_role = True
                role_names = ['Staff']
    else:
        user_roles = (
            UserRole.objects
            .filter(user=user)
            .select_related('role')
        )
        role_names = [ur.role.name for ur in user_roles]
        role_slugs = [ur.role.slug for ur in user_roles]

        for ur in user_roles:
            for rp in ur.role.role_permissions.select_related('permission').all():
                perms.add(rp.permission.codename)

        is_admin_role = any(s in ('super-admin', 'owner', 'administrator') for s in role_slugs)
        is_teacher_role = any(s == 'muellim' for s in role_slugs)
        is_student_role = any(s == 'telebe' for s in role_slugs)

        # Fallback: profile-based roles
        if not role_names:
            if hasattr(user, 'teacher_profile'):
                is_teacher_role = True
                role_names = ['Müəllim']
                perms = {
                    'view_students', 'view_teachers', 'view_courses', 'view_groups',
                    'edit_groups', 'view_payments', 'view_attendance', 'add_attendance',
                    'edit_attendance', 'view_exams', 'add_exams', 'grade_exams', 'view_notifications',
                }
            elif hasattr(user, 'student_profile'):
                is_student_role = True
                role_names = ['Tələbə']
                perms = {
                    'view_courses', 'view_groups', 'view_attendance', 'view_payments',
                    'view_exams', 'view_notifications',
                }
            elif hasattr(user, 'employee_profile'):
                is_admin_role = True
                role_names = ['İşçi']

    # ── Role booleans ──
    ctx['is_super'] = is_super
    ctx['is_staff_user'] = is_staff and not is_super
    ctx['is_admin_role'] = is_admin_role
    ctx['is_teacher_role'] = is_teacher_role
    ctx['is_student_role'] = is_student_role
    ctx['user_role_names'] = role_names
    ctx['user_permissions'] = perms
    # ── Sidebar section flags ──
    p = perms
    if is_teacher_role:
        ctx['can_see_users'] = False
        ctx['can_see_students'] = False
        ctx['can_see_teachers'] = False
        ctx['can_see_courses'] = False
        ctx['can_see_groups'] = True
        ctx['can_see_payments'] = False
        ctx['can_see_attendance'] = False
        ctx['can_see_exams'] = False
        ctx['can_see_online_exams'] = False
        ctx['can_see_schedule'] = False
        ctx['can_see_employees'] = False
        ctx['can_see_roles'] = False
        ctx['can_see_settings'] = False
        ctx['show_section_finance'] = False
        ctx['show_section_operations'] = False
        ctx['show_section_system'] = False
    elif is_student_role:
        ctx['can_see_users'] = False
        ctx['can_see_students'] = False
        ctx['can_see_teachers'] = False
        ctx['can_see_courses'] = False
        ctx['can_see_groups'] = True
        ctx['can_see_payments'] = False
        ctx['can_see_attendance'] = False
        ctx['can_see_exams'] = False
        ctx['can_see_online_exams'] = False
        ctx['can_see_schedule'] = False
        ctx['can_see_employees'] = False
        ctx['can_see_roles'] = False
        ctx['can_see_settings'] = False
    else:
        ctx['can_see_users'] = is_super or is_admin_role
        ctx['can_see_students'] = is_super or is_admin_role or 'view_students' in p
        ctx['can_see_teachers'] = is_super or is_admin_role or 'view_teachers' in p
        ctx['can_see_courses'] = is_super or is_admin_role or 'view_courses' in p
        ctx['can_see_groups'] = is_super or is_admin_role or 'view_groups' in p
        ctx['can_see_payments'] = is_super or is_admin_role or 'view_payments' in p
        ctx['can_see_attendance'] = is_super or is_admin_role or 'view_attendance' in p
        ctx['can_see_exams'] = is_super or is_admin_role
        ctx['can_see_online_exams'] = False
        ctx['can_see_schedule'] = False
        ctx['can_see_employees'] = is_super or is_admin_role
        ctx['can_see_roles'] = False
        ctx['can_see_settings'] = False
        ctx['show_section_finance'] = False
        ctx['show_section_operations'] = False
        ctx['show_section_system'] = False

    return ctx
