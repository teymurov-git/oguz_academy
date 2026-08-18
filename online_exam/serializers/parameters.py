from rest_framework import serializers
from ..models import (
    ExamType, Subject, Sinif, Bolme, Qrup, District,
    SchoolType, School, Universities, PreviousExam,
)


class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class SinifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sinif
        fields = "__all__"


class BolmeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bolme
        fields = "__all__"


class QrupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qrup
        fields = "__all__"


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class SchoolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolType
        fields = "__all__"


class SchoolSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.district_name", read_only=True, default="")
    school_type_name = serializers.CharField(source="school_type.school_type_name", read_only=True, default="")

    class Meta:
        model = School
        fields = "__all__"


class UniversitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universities
        fields = "__all__"


class PreviousExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreviousExam
        fields = "__all__"
