from django import forms
from attendance.models import Attendance


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ['student', 'group', 'lesson_date', 'status', 'late_minutes', 'reason']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'lesson_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'late_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
