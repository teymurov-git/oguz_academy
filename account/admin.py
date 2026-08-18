from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from account.models import User, BlockIpAdress
from oguz.admin_site import admin_site


ROLE_CHOICES = [
    ('', '-- Rol seçin --'),
    ('admin', 'Admin'),
    ('super_user', 'Super İstifadəçi'),
    ('teacher', 'Müəllim'),
]


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Rol',
        required=True,
        widget=forms.Select(attrs={
            'class': 'otm-input',
            'style': 'width:100%;padding:10px 14px;background:var(--bg-primary);border:1px solid var(--border);border-radius:10px;color:var(--text-primary);font-size:14px;font-family:inherit;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'12\' height=\'12\' fill=\'none\' stroke=\'%236b7280\' stroke-width=\'2\'%3E%3Cpath d=\'M2 4l4 4 4-4\'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;cursor:pointer',
        }),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        if role == 'super_user':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'teacher':
            user.is_staff = True
        if commit:
            user.save()
            if role == 'teacher':
                from teachers.models import Teacher
                from roles.models import Role, UserRole
                Teacher.objects.get_or_create(user=user)
                muellim_role = Role.objects.filter(slug='muellim').first()
                if muellim_role:
                    UserRole.objects.get_or_create(user=user, role=muellim_role)
        return user


class UserAdminCustom(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = UserChangeForm
    list_display = ('email', 'username', 'first_name', 'last_name', 'phone', 'is_active', 'is_staff', 'is_superuser', 'role_badge')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Şəxsi Məlumatlar', {'fields': ('first_name', 'last_name', 'username', 'phone', 'photo', 'bio')}),
        ('İcazələr', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Vacib Tarixlər', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'username', 'phone', 'role', 'password1', 'password2'),
        }),
    )

    def role_badge(self, obj):
        from roles.models import UserRole
        roles = list(UserRole.objects.filter(user=obj).select_related('role'))
        badges = []
        role_colors = {
            'Super Admin': ('purple', 'Super Admin'),
            'Owner': ('blue', 'Owner'),
            'Administrator': ('amber', 'Admin'),
            'Müəllim': ('green', 'Müəllim'),
            'Tələbə': ('gray', 'Tələbə'),
        }
        for ur in roles:
            role_name = ur.role.name
            if role_name in role_colors:
                css, label = role_colors[role_name]
            else:
                css, label = 'gray', role_name
            badges.append(f'<span class="otm-badge {css}">{label}</span>')
        if not badges:
            if obj.is_superuser:
                badges.append('<span class="otm-badge purple">Super Admin</span>')
            elif obj.is_staff:
                badges.append('<span class="otm-badge blue">Staff</span>')
            else:
                badges.append('<span class="otm-badge gray">—</span>')
        return ' '.join(badges)
    role_badge.short_description = 'Rol'
    role_badge.allow_tags = True

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_staff and not obj.is_superuser:
            from roles.models import UserRole, Role
            has_teacher_role = UserRole.objects.filter(
                user=obj, role__slug='muellim'
            ).exists()
            if has_teacher_role or hasattr(obj, 'teacher_profile'):
                from teachers.models import Teacher
                Teacher.objects.get_or_create(user=obj)
                muellim_role = Role.objects.filter(slug='muellim').first()
                if muellim_role:
                    UserRole.objects.get_or_create(user=obj, role=muellim_role)


class BlockIpAdressAdmin(admin.ModelAdmin):
    list_display = ('ip_address',)


admin_site.register(User, UserAdminCustom)
admin_site.register(BlockIpAdress, BlockIpAdressAdmin)