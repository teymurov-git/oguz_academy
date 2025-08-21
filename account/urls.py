from django.contrib import admin
from django.urls import path
from account.views import login, register, profile

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile')
]