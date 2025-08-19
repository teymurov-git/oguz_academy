from django.contrib import admin
from django.urls import path
from courses.views import abiturient, django, informatics, language, lyceum, middleschool, miq, python

urlpatterns = [
    path('abiturient/', abiturient, name='abiturient'),
    path('django/', django, name='django'),
    path('informatics/', informatics, name='informatics'),
    path('language/', language, name='language'),
    path('lyceum/', lyceum, name='lyceum'),
    path('middleschool/', middleschool, name='middleschool'),
    path('miq/', miq, name='miq'),
    path('python/', python, name='python'),
]