import uuid
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from students.models import Student, Parent
from teachers.models import Teacher
from courses.models import AcademicYear
from oguz.admin_site import admin_site

User = get_user_model()


def get_current_year_id(request):
    return request.session.get('academic_year_id')


class StudentAdminForm(forms.ModelForm):
    first_name = forms.CharField(label='Ad', max_length=150)
    last_name = forms.CharField(label='Soyad', max_length=150)
    teachers = forms.ModelMultipleChoiceField(
        label='Müəllimlər',
        queryset=Teacher.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Müəllimlər', is_stacked=False),
    )

    class Meta:
        model = Student
        fields = (
            'first_name', 'last_name', 'phone', 'parent_phone', 'date_of_birth',
            'monthly_payment', 'teachers', 'enrollment_date',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['teachers'].initial = self.instance.teachers.all()

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
            username = f"stu-{uuid.uuid4().hex[:8]}"
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
            self.save_m2m()

        return instance


class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ('user', 'student_id', 'phone', 'status', 'is_active', 'payment_status', 'enrollment_date')
    list_filter = ('status', 'is_active', 'gender', 'payment_status', 'academic_year')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'student_id', 'phone')
    readonly_fields = ('student_id',)
    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('first_name', 'last_name', 'phone', 'parent_phone', 'date_of_birth', 'enrollment_date')
        }),
        ('Ödəniş', {
            'fields': ('monthly_payment',)
        }),
        ('Müəllimlər', {
            'fields': ('teachers',)
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


class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'occupation', 'is_primary')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone')
    raw_id_fields = ('user',)
    list_filter = ('is_primary',)


admin_site.register(Student, StudentAdmin)
admin_site.register(Parent, ParentAdmin)
