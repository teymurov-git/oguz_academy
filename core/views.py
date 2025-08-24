from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from core.forms import ContactForm

from django.views.generic import CreateView

# Create your views here.


def home(request):
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact.html')

class ContactView(CreateView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        messages.success(self.request, 'Messages has sent to succesfull!')
        return super().form_valid(form)

def events(request):
    return render(request, 'events.html')

def search(request):
    return render(request, 'search.html')

def about(request):
    return render(request, 'about.html')