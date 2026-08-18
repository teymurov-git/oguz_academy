from rest_framework import viewsets, serializers
from homework.models import Homework, HomeworkSubmission


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = '__all__'


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = '__all__'


class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.select_related('lesson', 'group', 'teacher').all()
    serializer_class = HomeworkSerializer


class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    queryset = HomeworkSubmission.objects.select_related('homework', 'student__user', 'graded_by').all()
    serializer_class = HomeworkSubmissionSerializer
