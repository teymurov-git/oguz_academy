from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models.parameters import (
    ExamType, Subject, Sinif, Bolme, Qrup, District,
    SchoolType, School, Universities, PreviousExam,
)
from ..serializers.parameters import (
    ExamTypeSerializer, SubjectSerializer, SinifSerializer,
    BolmeSerializer, QrupSerializer, DistrictSerializer,
    SchoolTypeSerializer, SchoolSerializer, UniversitiesSerializer,
    PreviousExamSerializer,
)


class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    search_fields = ["exam_type_name"]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    search_fields = ["subject_name"]


class SinifViewSet(viewsets.ModelViewSet):
    queryset = Sinif.objects.all()
    serializer_class = SinifSerializer
    search_fields = ["sinif_name"]


class BolmeViewSet(viewsets.ModelViewSet):
    queryset = Bolme.objects.all()
    serializer_class = BolmeSerializer
    search_fields = ["bolme_name"]


class QrupViewSet(viewsets.ModelViewSet):
    queryset = Qrup.objects.all()
    serializer_class = QrupSerializer
    search_fields = ["qrup_name"]


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    search_fields = ["district_name"]


class SchoolTypeViewSet(viewsets.ModelViewSet):
    queryset = SchoolType.objects.all()
    serializer_class = SchoolTypeSerializer
    search_fields = ["school_type_name"]


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.select_related("district", "school_type").all()
    serializer_class = SchoolSerializer
    filterset_fields = ["district", "school_type"]
    search_fields = ["school_name"]


class UniversitiesViewSet(viewsets.ModelViewSet):
    queryset = Universities.objects.all()
    serializer_class = UniversitiesSerializer
    search_fields = ["university_name"]


class PreviousExamViewSet(viewsets.ModelViewSet):
    queryset = PreviousExam.objects.all()
    serializer_class = PreviousExamSerializer
    search_fields = ["prev_exam_name"]
