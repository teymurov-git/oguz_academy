from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.auth.forms import AuthenticationForm, UsernameField

class LoginForm(AuthenticationForm):

    username = UsernameField(widget=forms.TextInput(attrs={
        'class' : 'form-control',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class' : 'form-control',
    }))



class RegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'phone',
            'email',
            'photo',
            'password'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            })
        }
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email ilə artıq hesab mövcuddur!")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'profile-input',
                'placeholder': 'Ad'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'profile-input',
                'placeholder': 'Soyad'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'profile-input',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'profile-input',
                'placeholder': 'Telefon'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'profile-input profile-textarea',
                'placeholder': 'Haqqınızda',
                'rows': 4
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'profile-input',
                'accept': 'image/*'
            }),
        }


class PasswordChangeCustomForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'profile-input',
            'placeholder': 'Cari şifrə'
        }),
        label='Cari şifrə'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'profile-input',
            'placeholder': 'Yeni şifrə'
        }),
        label='Yeni şifrə',
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'profile-input',
            'placeholder': 'Yeni şifrəni təsdiq edin'
        }),
        label='Şifrəni təsdiq edin'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Cari şifrə yanlışdır.')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Yeni şifrələr uyğun gəlmir.')
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()
        return self.user