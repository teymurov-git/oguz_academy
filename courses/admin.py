from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Sum
from courses.models import Exam, ExamRegistration, CourseCategory, Course, Group, GroupStudent, AcademicYear
from students.models import Student
from oguz.admin_site import admin_site


def _is_teacher(user):
    """Check if user is a teacher (has teacher_profile, not superuser)."""
    return not user.is_superuser and hasattr(user, 'teacher_profile')


class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'registration_deadline', 'academic_year', 'is_active')
    list_filter = ('is_active', 'date', 'academic_year')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Əsas', {'fields': ('title', 'slug', 'description', 'academic_year')}),
        ('Tarix', {'fields': ('date', 'registration_deadline')}),
        ('Qiymət', {'fields': ('price', 'max_participants', 'location')}),
        ('Status', {'fields': ('is_active',)}),
    )


class ExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'exam', 'registered_at')
    list_filter = ('exam', 'registered_at')
    search_fields = ('first_name', 'last_name', 'email')


class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'teacher', 'price', 'duration_weeks', 'is_active')
    list_filter = ('is_active', 'category', 'academic_year')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('teacher', 'category', 'academic_year')
    fieldsets = (
        ('Əsas', {'fields': ('name', 'slug', 'category', 'description')}),
        ('Müəllim', {'fields': ('teacher',)}),
        ('Maliyyə', {'fields': ('price', 'duration_weeks', 'lesson_count')}),
        ('Status', {'fields': ('is_active', 'academic_year')}),
        ('Əlavə', {'fields': ('thumbnail', 'installment_allowed', 'max_installments', 'curriculum', 'requirements'), 'classes': ('collapse',)}),
    )


class GroupAdminForm(forms.ModelForm):
    selected_students = forms.ModelMultipleChoiceField(
        label='Tələbələr',
        queryset=Student.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Tələbələr', is_stacked=False),
    )

    class Meta:
        model = Group
        fields = ('name', 'teacher', 'start_date', 'selected_students')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['selected_students'].initial = self.instance.students.all()


class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    list_display = ('name', 'course', 'teacher', 'type', 'status', 'start_date', 'student_count', 'total_earnings_display')
    list_filter = ('status', 'type', 'course', 'academic_year')
    search_fields = ('name', 'course__name')
    raw_id_fields = ('academic_year',)
    readonly_fields = ('total_earnings_display',)
    fieldsets = (
        ('Əsas', {'fields': ('name', 'teacher', 'start_date')}),
        ('Tələbələr', {'fields': ('selected_students',)}),
        ('Maliyyə', {'fields': ('total_earnings_display',)}),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        selected = form.cleaned_data.get('selected_students', [])
        current_ids = set(form.instance.students.values_list('id', flat=True))
        selected_ids = set(s.id for s in selected)
        for sid in selected_ids - current_ids:
            GroupStudent.objects.create(group=form.instance, student_id=sid)
        GroupStudent.objects.filter(group=form.instance, student_id__in=current_ids - selected_ids).delete()

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Tələbə'

    def total_earnings_display(self, obj):
        if obj.pk:
            total = obj.students.aggregate(Sum('monthly_payment'))['monthly_payment__sum'] or 0
            return f"{total:.2f} ₼"
        return "0.00 ₼"
    total_earnings_display.short_description = 'Ümumi qazanc (avtomatik)'

    def has_view_permission(self, request, obj=None):
        if _is_teacher(request.user):
            return True
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if _is_teacher(request.user):
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if _is_teacher(request.user):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if _is_teacher(request.user):
            return False
        return super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _is_teacher(request.user):
            qs = qs.filter(teacher=request.user.teacher_profile)
        return qs


class GroupStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'status', 'joined_at')
    list_filter = ('status',)
    raw_id_fields = ('student', 'group')

    def has_view_permission(self, request, obj=None):
        if _is_teacher(request.user):
            return True
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if _is_teacher(request.user):
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if _is_teacher(request.user):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if _is_teacher(request.user):
            return False
        return super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _is_teacher(request.user):
            qs = qs.filter(group__teacher=request.user.teacher_profile)
        return qs


class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('name',)


admin_site.register(Exam, ExamAdmin)
admin_site.register(ExamRegistration, ExamRegistrationAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(GroupStudent, GroupStudentAdmin)
admin_site.register(AcademicYear, AcademicYearAdmin)
