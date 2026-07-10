from django import forms
from attendance.models import Attendance


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ['group', 'student', 'date', 'status', 'note']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }
