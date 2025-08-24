from django.contrib import admin
from django.urls import path
from core.views import home, ContactView, search, about, events

urlpatterns = [
    path('', home, name='home'),
    path('contact/', ContactView.as_view(), name = 'contact'),
    path('search', search, name='search'),
    path('about', about, name='about'),
    path('events', events, name='events')
]