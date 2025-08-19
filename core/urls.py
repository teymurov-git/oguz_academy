from django.contrib import admin
from django.urls import path
from core.views import home, contact, search, about, events

urlpatterns = [
    path('', home, name='home'),
    path('contact', contact, name='contact'),
    path('search', search, name='search'),
    path('about', about, name='about'),
    path('events', events, name='events')
]