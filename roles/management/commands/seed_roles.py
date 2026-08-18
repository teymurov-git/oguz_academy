from django.core.management.base import BaseCommand
from roles.models import Role, Permission


ROLES = [
    {'name': 'Super Admin', 'slug': 'super-admin', 'description': 'Sistemin tam idarəetmə hüququ', 'is_system': True},
    {'name': 'Owner', 'slug': 'owner', 'description': 'Müəssisə sahibi, tam giriş', 'is_system': True},
    {'name': 'Administrator', 'slug': 'administrator', 'description': 'İdarəetmə panelinə tam giriş', 'is_system': True},
    {'name': 'Müəllim', 'slug': 'muellim', 'description': 'Qruplar, tələbələr, davamiyyət idarəsi', 'is_system': False},
    {'name': 'Tələbə', 'slug': 'telebe', 'description': 'Kurslar, imtahanlar, ödənişlər', 'is_system': False},
]

PERMISSIONS = [
    # Students
    {'codename': 'view_students', 'name': 'Tələbələrə baxmaq', 'module': 'students', 'action': 'view'},
    {'codename': 'add_students', 'name': 'Tələbə əlavə etmək', 'module': 'students', 'action': 'add'},
    {'codename': 'edit_students', 'name': 'Tələbə redaktə etmək', 'module': 'students', 'action': 'edit'},
    {'codename': 'delete_students', 'name': 'Tələbə silmək', 'module': 'students', 'action': 'delete'},
    # Teachers
    {'codename': 'view_teachers', 'name': 'Müəllimlərə baxmaq', 'module': 'teachers', 'action': 'view'},
    {'codename': 'add_teachers', 'name': 'Müəllim əlavə etmək', 'module': 'teachers', 'action': 'add'},
    {'codename': 'edit_teachers', 'name': 'Müəllim redaktə etmək', 'module': 'teachers', 'action': 'edit'},
    {'codename': 'delete_teachers', 'name': 'Müəllimi silmək', 'module': 'teachers', 'action': 'delete'},
    # Courses
    {'codename': 'view_courses', 'name': 'Kurslara baxmaq', 'module': 'courses', 'action': 'view'},
    {'codename': 'add_courses', 'name': 'Kurs yaratmaq', 'module': 'courses', 'action': 'add'},
    {'codename': 'edit_courses', 'name': 'Kurs redaktə etmək', 'module': 'courses', 'action': 'edit'},
    {'codename': 'delete_courses', 'name': 'Kurs silmək', 'module': 'courses', 'action': 'delete'},
    # Groups
    {'codename': 'view_groups', 'name': 'Qruplara baxmaq', 'module': 'groups', 'action': 'view'},
    {'codename': 'add_groups', 'name': 'Qrup yaratmaq', 'module': 'groups', 'action': 'add'},
    {'codename': 'edit_groups', 'name': 'Qrup redaktə etmək', 'module': 'groups', 'action': 'edit'},
    {'codename': 'delete_groups', 'name': 'Qrup silmək', 'module': 'groups', 'action': 'delete'},
    # Payments
    {'codename': 'view_payments', 'name': 'Ödənişlərə baxmaq', 'module': 'payments', 'action': 'view'},
    {'codename': 'add_payments', 'name': 'Ödəniş qəbul etmək', 'module': 'payments', 'action': 'add'},
    {'codename': 'edit_payments', 'name': 'Ödəniş redaktə etmək', 'module': 'payments', 'action': 'edit'},
    {'codename': 'delete_payments', 'name': 'Ödənişi silmək', 'module': 'payments', 'action': 'delete'},
    # Attendance
    {'codename': 'view_attendance', 'name': 'Davamiyyətə baxmaq', 'module': 'attendance', 'action': 'view'},
    {'codename': 'add_attendance', 'name': 'Davamiyyət qeyd etmək', 'module': 'attendance', 'action': 'add'},
    {'codename': 'edit_attendance', 'name': 'Davamiyyət redaktə etmək', 'module': 'attendance', 'action': 'edit'},
    # Reports
    {'codename': 'view_reports', 'name': 'Hesabatlara baxmaq', 'module': 'reports', 'action': 'view'},
    # Settings
    {'codename': 'view_settings', 'name': 'Parametrlərə baxmaq', 'module': 'settings', 'action': 'view'},
    {'codename': 'edit_settings', 'name': 'Parametrləri dəyişmək', 'module': 'settings', 'action': 'edit'},
    # Exams
    {'codename': 'view_exams', 'name': 'İmtahanlara baxmaq', 'module': 'exams', 'action': 'view'},
    {'codename': 'add_exams', 'name': 'İmtahan yaratmaq', 'module': 'exams', 'action': 'add'},
    {'codename': 'grade_exams', 'name': 'İmtahan qiymətləndirmək', 'module': 'exams', 'action': 'grade'},
    # Notifications
    {'codename': 'view_notifications', 'name': 'Bildirişlərə baxmaq', 'module': 'notifications', 'action': 'view'},
    {'codename': 'send_notifications', 'name': 'Bildiriş göndərmək', 'module': 'notifications', 'action': 'send'},
]

ROLE_PERMISSIONS = {
    'super-admin': [p['codename'] for p in PERMISSIONS],
    'owner': [p['codename'] for p in PERMISSIONS],
    'administrator': [p['codename'] for p in PERMISSIONS if p['codename'] != 'edit_settings'],
    'muellim': [
        'view_students', 'view_teachers', 'view_courses', 'view_groups',
        'edit_groups', 'view_payments', 'view_attendance', 'add_attendance', 'edit_attendance',
        'view_exams', 'add_exams', 'grade_exams', 'view_notifications',
    ],
    'telebe': [
        'view_courses', 'view_groups', 'view_attendance', 'view_payments', 'view_exams', 'view_notifications',
    ],
}


class Command(BaseCommand):
    help = 'Vercel app-ə uyğun rolları yaradır'

    def handle(self, *args, **options):
        self.stdout.write('Rollar yaradılır...')

        created_permissions = {}
        for perm_data in PERMISSIONS:
            perm, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults=perm_data,
            )
            created_permissions[perm.codename] = perm
            if created:
                self.stdout.write(f'  + İcazə yaradıldı: {perm.name}')
            else:
                self.stdout.write(f'  = İcazə artıq var: {perm.name}')

        self.stdout.write('')
        self.stdout.write('Rollar yaradılır...')

        for role_data in ROLES:
            role, created = Role.objects.get_or_create(
                slug=role_data['slug'],
                defaults=role_data,
            )
            if created:
                self.stdout.write(f'  + Rol yaradıldı: {role.name}')
            else:
                self.stdout.write(f'  = Rol artıq var: {role.name}')

            from roles.models import RolePermission
            codenames = ROLE_PERMISSIONS.get(role_data['slug'], [])
            for codename in codenames:
                if codename in created_permissions:
                    rp, rp_created = RolePermission.objects.get_or_create(
                        role=role,
                        permission=created_permissions[codename],
                    )
                    if rp_created:
                        self.stdout.write(f'    + {role.name} <- {codename}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Tamamlandı! Rollar yaradıldı.'))