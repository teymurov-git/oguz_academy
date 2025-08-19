from django.shortcuts import render

# Create your views here.

def abiturient(request):
    return render(request, 'abiturient.html')

def django(request):
    return render(request, 'django.html')

def informatics(request):
    return render(request, 'informatics.html')

def language(request):
    return render(request, 'language.html')

def lyceum(request):
    return render(request, 'lyceum.html')

def middleschool(request):
    return render(request, 'middleschool.html')

def miq(request):
    return render(request, 'miq.html')

def python(request):
    return render(request, 'python.html')
