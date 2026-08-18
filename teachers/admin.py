import uuid
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from teachers.models import Teacher
from students.models import Student
from courses.models import Group, AcademicYear
from oguz.admin_site import admin_site

User = get_user_model()


def get_current_year_id(request):
    return request.session.get('academic_year_id')


class TeacherAdminForm(forms.ModelForm):
    first_name = forms.CharField(label='Ad', max_length=150)
    last_name = forms.CharField(label='Soyad', max_length=150)
    students = forms.ModelMultipleChoiceField(
        label='Tələbələr',
        queryset=Student.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Tələbələr', is_stacked=False),
    )
    groups = forms.ModelMultipleChoiceField(
        label='Dərs dediyi qruplar',
        queryset=Group.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Qruplar', is_stacked=False),
    )

    class Meta:
        model = Teacher
        fields = (
            'first_name', 'last_name', 'patronymic', 'phone',
            'specialization', 'date_of_birth', 'students', 'groups',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['students'].initial = self.instance.students.all()
            self.fields['groups'].initial = self.instance.groups.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        if instance.pk and instance.user_id:
            user = instance.user
            user.first_name = first_name
            user.last_name = last_name
            if commit:
                user.save()
        else:
            username = f"tch-{uuid.uuid4().hex[:8]}"
            email = f"{username}@oguz.edu"
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            instance.user = user

        if commit:
            instance.save()
            selected_students = self.cleaned_data.get('students', [])
            instance.students.set(selected_students)
            selected_groups = self.cleaned_data.get('groups', [])
            Group.objects.filter(teacher=instance).exclude(id__in=[g.id for g in selected_groups]).update(teacher=None)
            Group.objects.filter(id__in=[g.id for g in selected_groups]).update(teacher=instance)

        return instance


class TeacherAdmin(admin.ModelAdmin):
    form = TeacherAdminForm
    list_display = ('user', 'teacher_id', 'specialization', 'phone', 'hourly_rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'specialization', 'academic_year')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'teacher_id', 'specialization')
    readonly_fields = ('teacher_id',)
    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('first_name', 'last_name', 'patronymic', 'phone', 'date_of_birth')
        }),
        ('Peşəkar Məlumatlar', {
            'fields': ('specialization',)
        }),
        ('Qruplar', {
            'fields': ('groups',)
        }),
        ('Tələbələr', {
            'fields': ('students',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        year_id = get_current_year_id(request)
        if year_id:
            qs = qs.filter(academic_year_id=year_id)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            year_id = get_current_year_id(request)
            if year_id:
                obj.academic_year_id = year_id
        super().save_model(request, obj, form, change)


admin_site.register(Teacher, TeacherAdmin)
