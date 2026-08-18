from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView
from account.forms import RegisterForm, ProfileEditForm, PasswordChangeCustomForm


class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Qeydiyyat uğurla tamamlandı! Hesabınıza daxil olun.')
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)


class UserSignInView(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    return redirect('/')


class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.request.user
        context['profile_form'] = ProfileEditForm(instance=self.request.user)
        context['password_form'] = PasswordChangeCustomForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        if 'edit_profile' in request.POST:
            profile_form = ProfileEditForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profil yeniləndi!')
                return redirect('profile')
            context = self.get_context_data(**kwargs)
            context['profile_form'] = profile_form
            return self.render_to_response(context)
        elif 'change_password' in request.POST:
            password_form = PasswordChangeCustomForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Şifrə uğurla dəyişdirildi!')
                return redirect('profile')
            context = self.get_context_data(**kwargs)
            context['password_form'] = password_form
            return self.render_to_response(context)
        return redirect('profile')


def profile_view(request):
    return render(request, 'profile.html', {'profile_user': request.user})


def activate(request, uidb64, token):
    messages.success(request, 'Hesabınız aktivləşdirildi!')
    return redirect('login')
