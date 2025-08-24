from django.contrib import admin
from django.urls import path, re_path
from account.views import UserSignInView, register, profile, logout, activate

urlpatterns = [
    path('login/', UserSignInView.as_view(), name = 'login'),
    path('register/', register, name = 'register'),
    path('profile/', profile, name = 'profile'),
    path('logout/', logout, name = 'logout'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        activate, name='activate'),
]