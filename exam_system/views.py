from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from exam_system.models import (
    Exam, Question, Variant, StudentExam,
    StudentAnswer, MarkerConsensus, Competition
)
from exam_system.serializers import (
    ExamListSerializer, ExamDetailSerializer,
    QuestionSerializer, QuestionListSerializer,
    VariantSerializer, VariantDetailSerializer,
    StudentExamListSerializer, StudentExamDetailSerializer,
    StudentAnswerSerializer, StudentAnswerDetailSerializer,
    MarkerConsensusSerializer,
    CompetitionListSerializer, CompetitionDetailSerializer,
)


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('course', 'group', 'created_by').all()
    search_fields = ('title', 'subject', 'description')
    filterset_fields = ('exam_type', 'status', 'is_active')
    ordering_fields = ('created_at', 'start_datetime', 'title')

    def get_serializer_class(self):
        if self.action == 'list':
            return ExamListSerializer
        return ExamDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('exam').all()
    search_fields = ('text',)
    filterset_fields = ('exam', 'question_type', 'difficulty', 'is_active')
    ordering_fields = ('sort_order', 'created_at', 'difficulty')

    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionListSerializer
        return QuestionSerializer


class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.select_related('exam').prefetch_related('questions').all()
    search_fields = ('name', 'code')
    filterset_fields = ('exam', 'is_active')
    ordering_fields = ('sort_order', 'created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return VariantSerializer
        return VariantDetailSerializer


class StudentExamViewSet(viewsets.ModelViewSet):
    queryset = StudentExam.objects.select_related(
        'exam', 'student__user', 'variant'
    ).prefetch_related('answers__question').all()
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__user__email')
    filterset_fields = ('exam', 'status', 'passed')
    ordering_fields = ('created_at', 'score', 'completed_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentExamListSerializer
        return StudentExamDetailSerializer

    @action(detail=True, methods=['post'], url_path='start')
    def start_exam(self, request, pk=None):
        student_exam = self.get_object()
        if student_exam.status != 'registered':
            return Response({'detail': 'Bu imtahan artiq baslayib və ya bitib.'}, status=400)
        from django.utils import timezone
        student_exam.status = 'in_progress'
        student_exam.started_at = timezone.now()
        student_exam.save()
        return Response({'detail': 'İmtahan başladı.', 'started_at': student_exam.started_at})

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_exam(self, request, pk=None):
        student_exam = self.get_object()
        if student_exam.status != 'in_progress':
            return Response({'detail': 'Bu imtahan aktiv deyil.'}, status=400)
        from django.utils import timezone
        student_exam.status = 'completed'
        student_exam.completed_at = timezone.now()
        if student_exam.started_at:
            delta = student_exam.completed_at - student_exam.started_at
            student_exam.time_spent_seconds = int(delta.total_seconds())
        answers = student_exam.answers.all()
        total = sum(a.points_earned for a in answers)
        max_score = sum(a.question.points for a in answers)
        student_exam.score = total
        student_exam.percentage = (total / max_score * 100) if max_score > 0 else 0
        student_exam.passed = student_exam.percentage >= (student_exam.exam.passing_score / student_exam.exam.max_score * 100) if student_exam.exam.max_score > 0 else False
        student_exam.save()
        return Response({
            'detail': 'İmtahan tamamlandı.',
            'score': student_exam.score,
            'percentage': student_exam.percentage,
            'passed': student_exam.passed,
        })


class StudentAnswerViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswer.objects.select_related(
        'student_exam', 'question'
    ).all()
    filterset_fields = ('student_exam', 'question', 'is_correct')
    ordering_fields = ('answered_at',)

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentAnswerSerializer
        return StudentAnswerDetailSerializer


class MarkerConsensusViewSet(viewsets.ModelViewSet):
    queryset = MarkerConsensus.objects.select_related(
        'student_answer__student_exam', 'marker1_user', 'marker2_user', 'marker3_user'
    ).all()
    filterset_fields = ('is_resolved',)
    ordering_fields = ('created_at',)

    serializer_class = MarkerConsensusSerializer

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve_consensus(self, request, pk=None):
        consensus = self.get_object()
        final = consensus.calculate_final_score()
        if final is not None:
            return Response({'detail': 'Konsensus həll olundu.', 'final_score': final})
        return Response({'detail': 'Hələ bütün markerlər qiymətləndirməyib.'}, status=400)


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.prefetch_related('exams').all()
    search_fields = ('title', 'description')
    filterset_fields = ('status', 'is_active')
    ordering_fields = ('created_at', 'start_datetime')

    def get_serializer_class(self):
        if self.action == 'list':
            return CompetitionListSerializer
        return CompetitionDetailSerializer
