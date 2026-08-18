from django import forms
from django.contrib.auth import get_user_model

from students.models import Student

User = get_user_model()


class StudentForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='Ad', max_length=150, required=True)
    last_name = forms.CharField(label='Soyad', max_length=150, required=True)

    class Meta:
        model = Student
        fields = ['phone', 'address', 'date_of_birth', 'school', 'grade_level', 'gender', 'emergency_phone', 'status', 'is_active']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'grade_level': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        if self.instance.pk:
            user = self.instance.user
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        if not instance.pk:
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='default123',
            )
            instance.user = user
        else:
            user = instance.user
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        if commit:
            instance.save()
        return instance
