from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from account.forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required

# Create your views here.

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from account.tokens import account_activation_token

from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.views import LoginView

class UserSignInView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm

# def signin(request):
#     next = request.GET.get('next', reverse_lazy('home'))
#     form = LoginForm(request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
#             if user is not None:
#                 django_login(request, user)
#                 return redirect(next)
#             else:
#                 messages.error(request, 'Enter your valid information!')
#         else:
#             messages.error(request, 'Form is not valid!')
#     context = {'form': form}
#     return render(request, 'signin.html', context)


from django.shortcuts import render, redirect
from .forms import RegisterForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Əgər Profile modelində şəkil saxlanırsa:
            return redirect("login")  # qeydiyyatdan sonra login səhifəsinə yönləndir
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})



# def register(request):
#     if request.method == 'POST':
#         form = RegisterForm(data=request.POST, files=request.FILES)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])  
#             user.is_active = False  
#             user.save()
#             current_site = get_current_site(request)
#             subject = 'Activate Your MySite Account'
#             message = render_to_string('account_activation_email.html', {
#                 'user': user,
#                 'domain': current_site.domain,
#                 'uid': urlsafe_base64_encode(force_bytes(user.id)),
#                 'token': account_activation_token.make_token(user),
#             })
#             user.email_user(subject, message)
#             messages.success(request, 'Signup process is completed!')
#             return redirect('login')  
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = RegisterForm()

#     context = {'form': form}
#     return render(request, 'register.html', context)


def logout(request):
    django_logout(request)
    return redirect(reverse_lazy('login'))

@login_required
def profile(request):
    return render(request, 'profile.html')



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
    else:
        return render(request, 'account_activation_invalid.html')