from rest_framework import serializers
from ..models import (
    Competition, CompetitionQuestion, CompetitionParticipant,
    CompetitionQuestionAttempt,
)


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = "__all__"


class CompetitionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionQuestion
        fields = "__all__"


class CompetitionParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionParticipant
        fields = "__all__"


class CompetitionQuestionAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionQuestionAttempt
        fields = "__all__"
