from django import forms
from courses.models import ExamRegistration, Course, Group


class ExamRegistrationForm(forms.ModelForm):

    class Meta:
        model = ExamRegistration
        fields = ['first_name', 'last_name', 'email', 'phone', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ad'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Soyad'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-poçt'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefon nömrəsi'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Əlavə məlumat (istəyə bağlı)',
                'rows': 3
            }),
        }


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['name', 'description', 'price', 'duration_weeks', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duration_weeks': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ['name', 'course', 'teacher', 'schedule_text', 'start_date', 'end_date', 'max_students', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'schedule_text': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
