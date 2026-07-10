from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from account.forms import RegisterForm, LoginForm
from account.tokens import account_activation_token

User = get_user_model()


class UserSignInView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm


class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        django_login(request, user)
        return redirect('home')
    return render(request, 'account_activation_invalid.html')