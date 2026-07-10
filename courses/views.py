from django.views.generic import TemplateView


class AbiturientView(TemplateView):
    template_name = 'abiturient.html'


class DjangoView(TemplateView):
    template_name = 'django.html'


class InformaticsView(TemplateView):
    template_name = 'informatics.html'


class LanguageView(TemplateView):
    template_name = 'language.html'


class LyceumView(TemplateView):
    template_name = 'lyceum.html'


class MiddleSchoolView(TemplateView):
    template_name = 'middle-school.html'


class MiqView(TemplateView):
    template_name = 'miq.html'


class PythonView(TemplateView):
    template_name = 'python.html'
