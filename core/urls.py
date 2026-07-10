from django.urls import path
from core.views import HomeView, AboutView, EventsView, SearchView, ContactView, DashboardView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about', AboutView.as_view(), name='about'),
    path('events', EventsView.as_view(), name='events'),
    path('search', SearchView.as_view(), name='search'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]