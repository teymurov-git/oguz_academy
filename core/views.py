from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, CreateView

from core.forms import ContactForm


class HomeView(TemplateView):
    template_name = 'index.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class EventsView(TemplateView):
    template_name = 'events.html'


class SearchView(TemplateView):
    template_name = 'search.html'


class ContactView(CreateView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        messages.success(self.request, 'Message sent successfully!')
        return super().form_valid(form)