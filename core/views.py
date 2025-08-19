from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact.html')

def events(request):
    return render(request, 'events.html')

def search(request):
    return render(request, 'search.html')

def about(request):
    return render(request, 'about.html')