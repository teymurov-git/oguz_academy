from django.urls import path
from courses.views import (
    AbiturientView, DjangoView, InformaticsView, LanguageView,
    LyceumView, MiddleSchoolView, MiqView, PythonView,
)

urlpatterns = [
    path('abiturient/', AbiturientView.as_view(), name='abiturient'),
    path('django/', DjangoView.as_view(), name='django'),
    path('informatics/', InformaticsView.as_view(), name='informatics'),
    path('language/', LanguageView.as_view(), name='language'),
    path('lyceum/', LyceumView.as_view(), name='lyceum'),
    path('middleschool/', MiddleSchoolView.as_view(), name='middleschool'),
    path('miq/', MiqView.as_view(), name='miq'),
    path('python/', PythonView.as_view(), name='python'),
]