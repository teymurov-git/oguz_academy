from rest_framework import serializers
from ..models import (
    Marker, QuestionAssignment, StudentAnswerGrading,
    IndividualGrade, MarkerAnswerGrade,
)


class MarkerSerializer(serializers.ModelSerializer):
    is_head_marker = serializers.BooleanField(read_only=True)

    class Meta:
        model = Marker
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        marker = Marker(**validated_data)
        if password:
            marker.set_password(password)
        marker.save()
        return marker

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MarkerListSerializer(serializers.ModelSerializer):
    is_head_marker = serializers.BooleanField(read_only=True)

    class Meta:
        model = Marker
        fields = ["id", "name", "email", "role", "is_head_marker", "is_active", "last_login_at"]


class QuestionAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAssignment
        fields = "__all__"


class StudentAnswerGradingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswerGrading
        fields = "__all__"


class IndividualGradeSerializer(serializers.ModelSerializer):
    marker_name = serializers.CharField(source="marker.name", read_only=True, default="")

    class Meta:
        model = IndividualGrade
        fields = "__all__"


class MarkerAnswerGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkerAnswerGrade
        fields = "__all__"
