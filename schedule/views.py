from rest_framework import viewsets, serializers
from schedule.models import Schedule, Lesson, LessonAttendance


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class LessonAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonAttendance
        fields = '__all__'


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('group', 'schedule', 'teacher', 'room').all()
    serializer_class = LessonSerializer


class LessonAttendanceViewSet(viewsets.ModelViewSet):
    queryset = LessonAttendance.objects.select_related('lesson', 'student__user').all()
    serializer_class = LessonAttendanceSerializer
